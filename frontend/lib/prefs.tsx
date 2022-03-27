import { createContext, Dispatch, SetStateAction, useState } from "react"

export type Prefs = {
  dateAbsolute: boolean
  setPrefs: Dispatch<SetStateAction<Prefs>>
}

const defaultPrefs: Prefs = {
  dateAbsolute: false,
  setPrefs: () => {
    throw new Error("no setPrefs set")
  },
}

const PrefsCtx = createContext<Prefs>(defaultPrefs)

interface IPrefsProvider {
  children: React.ReactNode
}

export const PrefsProvider: React.FC<IPrefsProvider> = ({ children }: IPrefsProvider) => {
  const [prefs, setPrefs] = useState<Prefs>(defaultPrefs)
  return <PrefsCtx.Provider value={{ ...prefs, setPrefs }}>{children}</PrefsCtx.Provider>
}

const PrefsConsumer = PrefsCtx.Consumer

export default PrefsConsumer
