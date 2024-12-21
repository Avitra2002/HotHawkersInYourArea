import React from 'react'
import Hero from "../components/Hero"
import HomeCards from "../components/HomeCards"
import HawkerListings from "../components/HawkerListings"
import ViewAllHawkers from "../components/ViewAllHawkers"

const HomePage = () => {
  return (
    <>
      <Hero />
      <HomeCards />
      <HawkerListings isHome = {true}/>
      <ViewAllHawkers />
    </>
  )
}

export default HomePage