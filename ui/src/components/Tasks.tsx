import React, {ChangeEvent, FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {RouteComponentProps} from 'react-router'
import classnames from 'classnames'
import splitString from 'split-string'
import {DateTime} from 'luxon'

import {RootState, useAppDispatch} from '../store'
import {refreshTask, refreshTasks} from '../thunks/tasks'
import TaskListItem from './TaskListItem'
import TaskDetails from './TaskDetails'
import {Stream} from '../contexts/stream'
import {getMessage, StreamEventType} from '../clients/stream'
import {Task, TaskArrayFieldTypes, TaskFieldTypes} from '../clients/tasks'
import {UdaDefinition} from '../clients/status'

interface MatchParams {
  taskId: string
}

interface FilterParams {
  fields: {
    [key: string]: string
  }
  arrayFields: {
    [key: string]: string
  }
  udas: {
    [key: string]: string
  }
  description: string[]
  tags: string[]
}

function tokenizeFilters(
  filterString: string,
  udas: UdaDefinition[]
): FilterParams {
  const valueTokens = splitString(filterString, {
    separator: ' ',
    quotes: ['"', "'"],
  })
  const filters: FilterParams = {
    fields: {
      status: 'pending',
    },
    arrayFields: {},
    udas: {},
    description: [],
    tags: [],
  }

  for (const token of valueTokens) {
    const colonPos = token.indexOf(':')
    if (token.slice(0, 1) === '+') {
      filters.tags.push(token.slice(1))
    } else if (colonPos > -1) {
      const key = token.slice(0, colonPos) as keyof Task
      let value = token.slice(colonPos + 1)
      if (
        (value.slice(0, 1) === "'" && value.slice(-1) === "'") ||
        (value.slice(0, 1) === '"' && value.slice(-1) === '"')
      ) {
        value = value.slice(1, -1)
      }

      if (
        filters.fields[key] !== undefined ||
        filters.arrayFields[key] !== undefined ||
        filters.udas[key] !== undefined
      ) {
        throw new Error(`Filter already specified for field '${key}'.`)
      }

      if (Object.keys(TaskFieldTypes).includes(key)) {
        filters.fields[key] = value
      } else if (Object.keys(TaskArrayFieldTypes).includes(key)) {
        filters.arrayFields[key] = value
      } else if (udas.filter((uda) => uda.field === key).length) {
        filters.udas[key] = value
      } else {
        throw new Error(`Field '${key}' does not exist.`)
      }
    } else if (token.length > 0) {
      filters.description.push(token)
    }
  }

  return filters
}

function filterNumberCompare(filter: any, field: any): boolean {
  const targetValue = parseInt(filter, 10)
  const fieldValue = parseInt(field, 10)

  return targetValue === fieldValue
}

function filterStringCompare(filter: any, field: any): boolean {
  const targetValue = (filter as string).toLowerCase()
  const fieldValue = (field ? field.toString() : '').toLowerCase()

  return targetValue === fieldValue
}

function filterDateCompare(filter: any, field: any): boolean {
  let targetValue = filter as string
  const fieldValue = (field || '') as string

  if (targetValue === 'today') {
    targetValue = DateTime.local().toISO().slice(0, 10)
  } else if (targetValue === 'tomorrow') {
    targetValue = DateTime.local().plus({days: 1}).toISO().slice(0, 10)
  }

  return fieldValue.startsWith(targetValue)
}

function applyFilters(
  filters: FilterParams,
  tasks: Task[],
  udas: UdaDefinition[]
): Task[] {
  const filteredTasks: Task[] = []

  const handlers: {
    [key: string]: ((filter: string, field: any) => boolean) | undefined
  } = {
    string: filterStringCompare,
    numeric: filterNumberCompare,
    date: filterDateCompare,
  }

  for (const task of tasks) {
    let include = true

    // Free description
    const description = filters.description.join(' ').toLowerCase()
    if (description) {
      if (task.description.toLowerCase().indexOf(description) === -1) {
        include = false
      }
    }

    // Tags
    if (include) {
      for (const tag of filters.tags) {
        if (!(task.tags ?? []).includes(tag)) {
          include = false
          break
        }
      }
    }

    // Direct field comparisons
    if (include) {
      for (const filterField in filters.fields) {
        const filterValue = filters.fields[filterField]
        const filterType = TaskFieldTypes[filterField]
        const handler = handlers[filterType]

        if (!handler) {
          throw new Error(
            `Could not find handler function for ${filterField}: ${filterType}`
          )
        }

        if (!handler(filterValue, task[filterField as keyof Task])) {
          include = false
          break
        }
      }
    }

    // Array field comparisons
    if (include) {
      for (const filterField in filters.arrayFields) {
        const filterValue = filters.fields[filterField]
        const filterType = TaskArrayFieldTypes[filterField]
        const handler = handlers[filterType]

        if (!handler) {
          throw new Error(
            `Could not find handler function for ${filterField}: ${filterType}`
          )
        }

        let anyMatches = false
        for (const arrayInstanceValue of task[
          filterField as keyof Task
        ] as Array<any>) {
          if (handler(filterValue, arrayInstanceValue)) {
            anyMatches = true
            break
          }
        }

        if (!anyMatches) {
          include = false
          break
        }
      }
    }

    // UDA comparisons
    if (include) {
      for (const filterField in filters.udas) {
        const filterValue = filters.fields[filterField]
        const filterType = udas.filter((uda) => uda.field === filterField)[0]
          .type
        const handler = handlers[filterType]

        if (!handler) {
          throw new Error(`Field type '${filterType}' is not supported`)
        }

        if (!handler(filterValue, task.udas[filterField])) {
          include = false
          break
        }
      }
    }

    if (include) {
      filteredTasks.push(task)
    }
  }

  return filteredTasks
}

interface Props extends RouteComponentProps<MatchParams> {}

const Tasks: FunctionComponent<Props> = ({match, ...rest}) => {
  const tasks = useSelector((state: RootState) => state.tasks)
  const selectedTaskId = match.params.taskId
  const task = match
    ? tasks?.filter((task) => task.uuid === selectedTaskId)[0]
    : null
  const dispatch = useAppDispatch()
  const stylesheet = useSelector((state: RootState) =>
    state.status.logged_in === true ? state.status.colorscheme : null
  )
  const user_udas = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.udas : []
  )
  const system_udas = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.udas : []
  )
  const streamState = React.useContext(Stream)
  const [filterString, setFilterString] = React.useState<string>('')
  const [filteredTasks, setFilteredTasks] = React.useState<Task[]>(tasks ?? [])
  const [filterError, setFilterError] = React.useState<string>('')

  React.useEffect(() => {
    if (streamState.stream) {
      streamState.stream.addEventListener(
        StreamEventType.TaskChanged,
        (evt: Event) => {
          const taskId = getMessage(StreamEventType.TaskChanged, evt)
          dispatch(refreshTask(taskId))
        }
      )
    }
  }, [streamState.stream])

  React.useEffect(() => {
    const stylesheetId = 'colorscheme-stylesheet'

    if (stylesheet) {
      const existing = document.getElementById(stylesheetId)
      if (existing) {
        existing.remove()
      }

      const sheet = document.createElement('link')
      sheet.rel = 'stylesheet'
      sheet.href = `/assets/colorschemes/${stylesheet}.css`
      sheet.id = stylesheetId
      document.head.appendChild(sheet)
    }
  }, [stylesheet])

  React.useEffect(() => {
    dispatch(refreshTasks())
  }, [])

  React.useEffect(() => {
    const allUdas = system_udas.concat(user_udas)

    try {
      const processedFilters = tokenizeFilters(filterString, allUdas)
      setFilteredTasks(applyFilters(processedFilters, tasks ?? [], allUdas))
    } catch (e) {
      setFilterError(e.message)
      return
    }
    setFilterError('')
  }, [filterString, tasks, system_udas, user_udas])

  function onChangeFilter(filterValue: ChangeEvent<HTMLInputElement>) {
    setFilterString(filterValue.target.value)
  }

  return (
    <>
      <div className="row full-width">
        <div id="list" className="task-list">
          <input
            id="filter-string"
            onChange={onChangeFilter}
            value={filterString}
            className={classnames({error: filterError.length > 0})}
          />
          {filterError && <div className="filter-error">{filterError}</div>}
          {tasks &&
            filteredTasks.map((task) => (
              <TaskListItem
                tasks={tasks}
                task={task}
                key={task.id}
                active={task.id === selectedTaskId}
              />
            ))}
        </div>
        {task && tasks && <TaskDetails tasks={tasks} task={task} />}
      </div>
    </>
  )
}

export default Tasks
