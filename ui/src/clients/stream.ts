import {createAction} from '@reduxjs/toolkit'

export enum StreamEventType {
  TaskChanged = 'task_changed',
  HeadChanged = 'head_changed',
  ErrorLogged = 'error_logged',
  Heartbeat = 'heartbeat',
  PublicAnnouncement = 'public_announcement',
  PersonalAnnouncement = 'personal_announcement',
}

export const StringMessageTypes = [
  StreamEventType.TaskChanged,
  StreamEventType.HeadChanged,
  StreamEventType.ErrorLogged,
]
export const MessageEventTypes = [
  StreamEventType.PublicAnnouncement,
  StreamEventType.PersonalAnnouncement,
]

export interface Message {
  type: 'info' | 'warning' | 'error' | 'success'
  title: string
  message: string
  duration?: number | null
}

export const createStream = (url: string, head: string | null): EventSource => {
  return new window.EventSource(url + (head ? `?head=${head}` : ''))
}

function normalizeMessageType(type: string | undefined): Message['type'] {
  if (type === 'warning') {
    return 'warning'
  } else if (type === 'error') {
    return 'error'
  } else if (type === 'success') {
    return 'success'
  }
  return 'info'
}

export function getMessage(
  messageType:
    | StreamEventType.TaskChanged
    | StreamEventType.HeadChanged
    | StreamEventType.ErrorLogged,
  evt: Event
): string
export function getMessage(
  messageType:
    | StreamEventType.PublicAnnouncement
    | StreamEventType.PersonalAnnouncement,
  evt: Event
): Message
export function getMessage(
  messageType: StreamEventType,
  evt: Event
): string | Message | undefined {
  const message = evt as MessageEvent

  if (StringMessageTypes.includes(messageType)) {
    return message.data
  }
  if (MessageEventTypes.includes(messageType)) {
    const rawMessage = JSON.parse(message.data)

    return {
      type: normalizeMessageType(rawMessage.type),
      title: rawMessage.title ?? '',
      message: rawMessage.message ?? '',
      duration: rawMessage.duration ?? undefined,
    }
  }

  return message.data
}

export default createStream
