import React from "react"

import styles from "../styles/Index.module.css"

type LayoutProps = React.PropsWithChildren<{}>

const Layout = ({ children }: LayoutProps) => {
  return <div className={styles.container}>{children}</div>
}

export default Layout
