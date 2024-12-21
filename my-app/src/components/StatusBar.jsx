import React, {useState, useEffect} from 'react'

const StatusBar = () => {
  const [currentCapacity, setCurrentCapacity] = useState(null); // New state for capacity
  
    useEffect(() => {
      const fetchData = async () => {
        try {
          const response = await fetch('/api/hawkers-data');
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          const data = await response.json();
          setCurrentCapacity(data.currentCapacity); // Fetch capacity from backend
        } catch (error) {
          console.error('Error fetching data:', error);
        }
      };
  
      fetchData();
    }, []);

  return (
    <section className="py-4">
      <div className="container-xl lg:container m-auto">
        <div className="grid grid-cols-1 gap-4 p-4 rounded-lg place-items-center">
          <div className="bg-gray-100 p-6 rounded-lg shadow-md">
            <div className="my-4">
                <h3 className="text-lg font-bold mb-2">Current Capacity</h3>
                {currentCapacity !== null ? (
                    <div className="w-full bg-gray-300 rounded-full h-6">
                    <div
                        className="bg-green-500 h-6 rounded-full"
                        style={{ width: `${currentCapacity}%` }}
                    ></div>
                    </div>
                ) : (
                    'Loading capacity...'
                )}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default StatusBar