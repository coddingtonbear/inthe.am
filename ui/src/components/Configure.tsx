import React, {FunctionComponent} from 'react'
import {RouteComponentProps} from 'react-router'
import {Tabs, TabItem, TabsContent, TabPanel} from 'react-foundation'
import {Link} from 'react-router-dom'

import Synchronization from './configure_pages/Synchronization'
import Trello from './configure_pages/Trello'
import Deduplication from './configure_pages/Deduplication'
import Zapier from './configure_pages/Zapier'
import ColorScheme from './configure_pages/ColorScheme'
import TaskRc from './configure_pages/TaskRc'
import ApiKeys from './configure_pages/ApiKeys'
import Feeds from './configure_pages/Feeds'
import Email from './configure_pages/Email'
import Sms from './configure_pages/Sms'
import DangerZone from './configure_pages/DangerZone'
import Footer from './Footer'

enum Page {
  Synchronization = 'synchronization',
  Trello = 'trello',
  Deduplication = 'deduplication',
  Zapier = 'zapier',
  ColorScheme = 'color-scheme',
  TaskRc = 'taskrc',
  API = 'api-keys',
  Feeds = 'feeds',
  Email = 'email',
  SMS = 'sms',
  DangerZone = 'danger-zone',
}

interface MatchParams {
  page: string
}

interface Props extends RouteComponentProps<MatchParams> {}

const Configure: FunctionComponent<Props> = ({match}) => {
  const page = match.params.page

  const tabInfo: {
    [key in Page]: {name: string; class?: string; component: FunctionComponent}
  } = {
    [Page.Synchronization]: {
      name: 'Synchronization',
      component: Synchronization,
    },
    [Page.Trello]: {name: 'Trello', component: Trello},
    [Page.Deduplication]: {name: 'Deduplication', component: Deduplication},
    [Page.Zapier]: {name: 'Zapier', class: 'beta', component: Zapier},
    [Page.ColorScheme]: {name: 'Color Scheme', component: ColorScheme},
    [Page.TaskRc]: {name: 'TaskRc Extras', component: TaskRc},
    [Page.API]: {name: 'API Keys', component: ApiKeys},
    [Page.Feeds]: {name: 'iCal & RSS Feeds', component: Feeds},
    [Page.Email]: {name: 'E-mail-to-Task', component: Email},
    [Page.SMS]: {name: 'SMS-to-Task', component: Sms},
    [Page.DangerZone]: {
      name: 'Danger Zone',
      class: 'red',
      component: DangerZone,
    },
  }

  const currentTab = tabInfo[match.params.page as keyof typeof tabInfo]

  return (
    <>
      <div className="row standalone">
        <div className="standalone grid-container">
          <div className="standalone-content grid-x">
            <div className="cell medium-3">
              <Tabs isVertical={true}>
                {Object.keys(tabInfo).map((keyName: string) => {
                  const tab = tabInfo[keyName as keyof typeof tabInfo]
                  return (
                    <TabItem isActive={page === keyName} key={keyName}>
                      <Link to={`/configure/${keyName}`}>{tab.name}</Link>
                    </TabItem>
                  )
                })}
              </Tabs>
            </div>
            <div className="cell medium-9">
              <TabsContent>
                <TabPanel isActive={true}>
                  <currentTab.component />
                </TabPanel>
              </TabsContent>
            </div>
          </div>
        </div>
        <Footer />
      </div>
    </>
  )
}

export default Configure
