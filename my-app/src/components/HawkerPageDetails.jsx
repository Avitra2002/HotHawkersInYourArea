import React from 'react'
import { Link } from 'react-router-dom'

const HawkerPageDetails = ({store}) => {
  return (
    <>
      <section>
       <div className="container m-auto py-6 px-6 flex justify-end">
        <Link
          to="/"
          className="text-indigo-500 hover:text-indigo-600 flex items-center"
        >
          <i className="fas fa-arrow-left mr-2"></i> Back to Homepage
        </Link>
       </div>
      </section>

      <section className="bg-indigo-50">
        <div className="container m-auto py-10 px-6">
          <div className="grid grid-cols-1 md:grid-cols-70/30 w-full gap-6">
            <main>
              <div
                className="bg-white p-6 rounded-lg shadow-md text-center md:text-left"
              >
                <h1 className="text-3xl font-bold mb-4">
                  {store.storeName}
                </h1>
                <div
                  className="text-gray-500 mb-4 flex align-middle justify-center md:justify-start"
                >
                  <i
                    className="fa-solid fa-location-dot text-lg text-orange-700 mr-2"
                  ></i>
                  <p className="text-orange-700">{store.location}</p>
                </div>
              </div>
  
              <div className="bg-white p-6 rounded-lg shadow-md mt-6">
                <h3 className="text-indigo-800 text-lg font-bold mb-6">
                  Store Description
                </h3>
  
                <p className="mb-4">
                  {store.description}
                </p>
  
                <h3 className="text-indigo-800 text-lg font-bold mb-2">Wait Time</h3>
  
                <h3 className="text-2xl text-yellow-500 mb-2">{store.averageDwellTime} mins</h3>
              </div>
            </main>
  
            <aside>
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-xl font-bold mb-6">Company Info</h3>
  
                <h2 className="text-2xl">NewTek Solutions</h2>
  
                <p className="my-2">
                  NewTek Solutions is a leading technology company specializing in web development and digital solutions. We pride ourselves on delivering high-quality products and services to our clients while fostering a collaborative and innovative work environment.
                </p>
  
                <hr className="my-4" />
  
                <h3 className="text-xl">Contact Email:</h3>
  
                <p className="my-2 bg-indigo-100 p-2 font-bold">
                  contact@newteksolutions.com
                </p>
  
                <h3 className="text-xl">Contact Phone:</h3>
  
                <p className="my-2 bg-indigo-100 p-2 font-bold">555-555-5555</p>
              </div>
  
              <div className="bg-white p-6 rounded-lg shadow-md mt-6">
                <h3 className="text-xl font-bold mb-6">Manage Job</h3>
                <a
                  href="/add-job.html"
                  className="bg-indigo-500 hover:bg-indigo-600 text-white text-center font-bold py-2 px-4 rounded-full w-full focus:outline-none focus:shadow-outline mt-4 block"
                  >Edit Job</a
                >
                <button
                  className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-full w-full focus:outline-none focus:shadow-outline mt-4 block"
                >
                  Delete Job
                </button>
              </div>
            </aside>
          </div>
        </div>
      </section>
      </>
  )
}

export default HawkerPageDetails