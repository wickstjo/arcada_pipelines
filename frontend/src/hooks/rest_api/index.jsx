import { useState, useEffect } from 'react'
import axios from 'axios'

const useApi = (url, transformer=undefined) => {

    // RESOURCE STATE
    const [resource, set_resource] = useState([])

    // ON LOAD, LOAD RESOURCE
    useEffect(() => {
        axios.get(url).then(response => {
            if (response.status === 200) {
                let data = response.data

                // IF A TRANSFORMER FUNC WAS DEFINED
                // AND THERE IS DATA TO PARSE
                if (transformer) {
                    data = transformer(data)
                }

                set_resource(data)
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