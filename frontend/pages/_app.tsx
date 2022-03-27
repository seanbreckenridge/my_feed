import "../styles/globals.css"
import "@fortawesome/fontawesome-svg-core/styles.css"

import { config } from "@fortawesome/fontawesome-svg-core"
import type { AppProps } from "next/app"
import React from "react"

import { PrefsProvider } from "../lib/prefs"
config.autoAddCss = false

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <PrefsProvider>
      <Component {...pageProps} />
    </PrefsProvider>
  )
}

export default MyApp
