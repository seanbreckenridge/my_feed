import "../styles/globals.css"
import "@fortawesome/fontawesome-svg-core/styles.css"

import { config } from "@fortawesome/fontawesome-svg-core"
import type { AppProps } from "next/app"
import React from "react"

import ErrorBoundary from "../components/ErrorBoundary"
import Layout from "../components/Layout"
import { PrefsProvider } from "../lib/prefs"
config.autoAddCss = false

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <PrefsProvider>
      <Layout>
        <ErrorBoundary>
          <Component {...pageProps} />
        </ErrorBoundary>
      </Layout>
    </PrefsProvider>
  )
}

export default MyApp
