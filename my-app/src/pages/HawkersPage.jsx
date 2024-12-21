import React from 'react'
import HawkerListings from '../components/HawkerListings'

const HawkersPage = () => {
  return (
    <>
    <section>
      <div className="container m-auto py-6 px-6 flex justify-end">
        <a
          href="/"
          className="text-indigo-500 hover:text-indigo-600 flex items-center"
        >
          <i className="fas fa-arrow-left mr-2"></i> Back to Homepage
        </a>
      </div>
    </section>

    <section className='bg-blue-50 px-4 py-6'>
        <HawkerListings />
    </section>
    </>
  )
}

export default HawkersPage