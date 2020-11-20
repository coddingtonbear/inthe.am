import React, {FormEvent, FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {useToasts} from 'react-toast-notifications'

import request from '../../clients/request'
import {RootState, useAppDispatch} from '../../store'
import {refreshStatus} from '../../thunks/status'

const ColorSchemes = [
  {file: 'light-16.theme', name: 'Light (4-bit)'},
  {file: 'dark-16.theme', name: 'Dark (4-bit)'},
  {file: 'light-256.theme', name: 'Light'},
  {file: 'dark-256.theme', name: 'Dark'},
  {file: 'dark-red-256.theme', name: 'Dark Red'},
  {file: 'dark-green-256.theme', name: 'Dark Green'},
  {file: 'dark-blue-256.theme', name: 'Dark Blue'},
  {file: 'dark-violets-256.theme', name: 'Dark Violet'},
  {file: 'dark-yellow-green.theme', name: 'Dark Yellow/Green'},
  {file: 'dark-gray-256.theme', name: 'Dark Gray'},
  {file: 'solarized-dark-256.theme', name: 'Solarized Dark'},
  {file: 'solarized-light-256.theme', name: 'Solarized Light'},
]

const ColorScheme: FunctionComponent = () => {
  const configColorScheme = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.colorscheme : ColorSchemes[0].file
  )
  const configColorUrl = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.urls?.set_colorscheme : null
  )
  const [colorScheme, setColorScheme] = React.useState<string>(
    configColorScheme
  )
  const {addToast} = useToasts()
  const dispatch = useAppDispatch()

  function onChange(event: FormEvent<HTMLSelectElement>) {
    event.preventDefault()

    const newValue = (event.target as HTMLSelectElement).value
    setColorScheme(newValue)

    if (!configColorUrl) {
      throw new Error('No color configuration URL found')
    }

    request('PUT', configColorUrl, {
      data: newValue,
      lookupApiUrl: false,
    }).then(() => {
      dispatch(refreshStatus())
      addToast('Colorscheme changed.', {appearance: 'success'})
    })
  }

  return (
    <div className="row">
      <div className="large-12 columns">
        <h3>Color Scheme</h3>
        Use the selector below to select a color scheme to use for your task
        list on Inthe.AM.
        <label>Color Scheme</label>
        <select onChange={onChange} value={colorScheme}>
          {ColorSchemes.map((entry) => (
            <option key={entry.file} value={entry.file}>
              {entry.name}
            </option>
          ))}
        </select>
        {/*
{{view "select" value=applicationController.user.colorscheme optionValuePath="content.file" optionLabelPath="content.name" content=themeOptions name="theme_selector"}}
<a href="" className="button radius" {{action "save_colorscheme"}}>Save Color Scheme</a>
      */}
      </div>
    </div>
  )
}

export default ColorScheme
