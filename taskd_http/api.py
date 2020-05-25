from datetime import datetime
import os
import subprocess
import tempfile
import uuid

from flask import Flask, request, redirect
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy


TASKD_BINARY = os.environ.get('TASKD_BINARY', '/usr/bin/taskd')
TASKD_DATA = os.environ['TASKDDATA']
CA_CERT = os.environ['CA_CERT']
CA_KEY = os.environ['CA_KEY']
CA_SIGNING_TEMPLATE = os.environ['CA_SIGNING_TEMPLATE']
CERT_DB_PATH = os.environ.get(
    'CERT_DB_PATH', 
    os.path.join(TASKD_DATA, 'certificates.sqlite3')
)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://' + CERT_DB_PATH
api = Api(app)

db = SQLAlchemy(app)


class Credential(db.Model):
    user_key = db.Column(db.String(36), nullable=False, primary_key=True)
    org_name = db.Column(db.String(255), nullable=False)
    user_name = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deleted = db.column(db.DateTime, nullable=True)

    def as_dict(self):
        return {
            'credentials': f'{self.org_name}/{self.user_name}/{self.user_key}',
        }


class Certificate(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    user_key = db.Column(db.String(36), nullable=False)
    certificate = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    revoked = db.Column(db.DateTime, nullable=True)

    def as_dict(self):
        return {
            'id': self.id,
            'certificate': self.certificate,
            'created': self.created,
            'revoked': self.revoked,
        }


class TaskdError(Exception):
    pass


class TaskdAccount(Resource):
    def put(self, org_name, user_name):
        env = os.environ.copy()
        env['TASKDDATA'] = TASKD_DATA

        command = [
            TASKD_BINARY,
            'add',
            'user',
            org_name,
            user_name
        ]
        key_proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        key_proc_output = (
            key_proc.communicate()[0].decode('utf-8').split('\n')
        )
        taskd_user_key = (
            key_proc_output[0].split(':')[1].strip()
        )
        result = key_proc.wait()
        if result != 0:
            raise TaskdError()

        cred = Credential(
            org_name=org_name,
            user_name=user_name,
            user_key=taskd_user_key,
        )
        db.session.add(cred)
        db.session.commit()

        return cred.as_dict()

    def get(self, org_name, user_name):
        cred = Credential.query.filter_by(
            user_name=user_name,
            org_name=org_name,
        ).first_or_404()

        return cred.as_dict()

    def delete(self, org_name, user_name):
        cred = Credential.query.filter_by(
            user_name=user_name,
            org_name=org_name,
        ).first_or_404()

        env = os.environ.copy()
        env['TASKDDATA'] = TASKD_DATA
        command = [
            TASKD_BINARY,
            'remove',
            'user',
            org_name,
            user_name
        ]
        delete_proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        result = delete_proc.wait()
        if result != 0:
            raise TaskdError()

        cred.deleted = datetime.utcnow()
        db.session.commit()

        return None


class TaskdCertificates(Resource):
    def post(self, org_name, user_name):
        with tempfile.NamedTemporaryFile('wb+') as outf:
            outf.write(request.data)
            outf.flush()

            cert_proc = subprocess.Popen(
                [
                    'certtool',
                    '--generate-certificate',
                    '--load-request',
                    outf.name,
                    '--load-ca-certificate',
                    CA_CERT,
                    '--load-ca-privkey',
                    CA_KEY,
                    '--template',
                    CA_SIGNING_TEMPLATE
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            cert = cert_proc.communicate()[0].decode('utf-8')

        cert_record = Certificate(
            org_name=org_name,
            user_name=user_name,
            certificate=cert,
        )
        db.session.add(cert_record)
        db.session.commit()

        return redirect(
            api.url_for(
                TaskdCertificateDetails,
                org_name=org_name,
                user_name=user_name,
                cert_id=cert_record.id,
            )
        )

    def get(self, org_name, user_name):
        return [
            record.as_dict()
            for record in Certificate.query.filter_by(
                user_name=user_name,
                org_name=org_name,
            )
        ]


class TaskdCertificateDetails(Resource):
    def get(self, org_name, user_name, cert_id):
        cert_record = Certificate.query.filter_by(
            user_name=user_name,
            org_name=org_name,
            id=cert_id,
        ).first_or_404()

        return cert_record.as_dict()

    def delete(self, org_name, user_name, cert_id):
        cert_record = Certificate.query.filter_by(
            user_name=user_name,
            org_name=org_name,
            id=cert_id,
        ).first_or_404()

        cert_record.revoked = datetime.utcnow()

        db.session.commit()

        return None


api.add_resource(TaskdAccount, '/<org_name>/<user_name>')
api.add_resource(TaskdCertificates, '/<org_name>/<user_name>/certificates/')
api.add_resource(
    TaskdCertificateDetails,
    '/<org_name>/<user_name>/certificates/<cert_id>'
)


if __name__ == '__main__':
    db.create_all()
    app.run(port=80, host='0.0.0.0')
