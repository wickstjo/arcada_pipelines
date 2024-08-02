import { useState, useEffect } from 'react'
import axios from 'axios'

const useApi = (url) => {

    // RESOURCE STATE
    const [resource, set_resource] = useState([])

    // ON LOAD, LOAD RESOURCE
    useEffect(() => {
        axios.get(url).then(response => {
            if (response.status === 200) {
                set_resource(response.data)
            }
        })
    }, [url])

    // CREATE NEW RESOURCE
    const create = async(payload) => {

        // PUSH ID & PERFORM QUERY
        payload.id = Number((Math.random() * 100000000).toFixed(0))
        const response = await axios.post(url, payload)

        // ALL OK
        if (response.status === 201) {

            // PUSH TO RESOURCES
            set_resource([
                ...resource,
                payload
            ])

            return true
        }

        return false
    }

    return [resource, {
        create
    }]
}

export default useApi