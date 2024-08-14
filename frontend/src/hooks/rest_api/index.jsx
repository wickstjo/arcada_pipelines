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
                return
            }

            console.log(response)
        })
    }, [url])

    // CREATE NEW RESOURCE
    const create = async() => {
        console.log('create trigger')
    }

    return [resource, {
        create
    }]
}

export default useApi