import "../styles/globals.css";
import type { AppProps } from "next/app";
import { config } from "@fortawesome/fontawesome-svg-core";
import "@fortawesome/fontawesome-svg-core/styles.css";
import React from "react";
import { NextQueryParamProvider } from "next-query-params";
import { PrefsProvider } from "../lib/prefs";
config.autoAddCss = false;

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <NextQueryParamProvider>
      <PrefsProvider>
        <Component {...pageProps} />
      </PrefsProvider>
    </NextQueryParamProvider>
  );
}

export default MyApp;
