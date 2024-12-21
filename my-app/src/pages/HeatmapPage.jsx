import React, {useState} from 'react'
import { Link } from 'react-router-dom'
import heatmap from "../assets/images/heatmap.png";
import StatusBar from '../components/StatusBar'
import Zones from '../components/Zones';

const HeatmapPage = () => {
  const [loading, setLoading] = useState(true)

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

    <section className="px-4 py-6 flex justify-center">
    <div className="w-full max-w-[700px]">
        <img
        src={heatmap}
        alt="Heatmap PNG"
        className="w-full h-auto object-contain"
        />
    </div>
    </section>

    <StatusBar />

    <section className='bg-blue-50 px-4 py-6'>
        <Zones />
    </section>
    </>
  )
}

export default HeatmapPage