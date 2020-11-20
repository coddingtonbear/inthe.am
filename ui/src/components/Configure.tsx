import React, {FunctionComponent} from 'react'
import {RouteComponentProps} from 'react-router'
import {Tabs, TabItem, TabsContent, TabPanel} from 'react-foundation'
import {Link} from 'react-router-dom'

import Synchronization from './configure_pages/Synchronization'
import Trello from './configure_pages/Trello'
import Deduplication from './configure_pages/Deduplication'

enum Page {
  Synchronization = 'synchronization',
  Trello = 'trello',
  Deduplication = 'deduplication',
  Zapier = 'zapier',
  UDAs = 'udas',
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
    [Page.Zapier]: {name: 'Zapier', class: 'beta', component: Synchronization},
    [Page.UDAs]: {name: 'UDAs', component: Synchronization},
    [Page.ColorScheme]: {name: 'Color Scheme', component: Synchronization},
    [Page.TaskRc]: {name: 'TaskRC', component: Synchronization},
    [Page.API]: {name: 'API Keys', component: Synchronization},
    [Page.Feeds]: {name: 'iCal & RSS Feeds', component: Synchronization},
    [Page.Email]: {name: 'E-mail-to-Task', component: Synchronization},
    [Page.SMS]: {name: 'SMS-to-Task', component: Synchronization},
    [Page.DangerZone]: {
      name: 'Danger Zone',
      class: 'red',
      component: Synchronization,
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
      </div>
    </>
  )
}

export default Configure
