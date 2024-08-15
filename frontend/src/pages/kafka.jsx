import { useEffect } from 'react'
import { useDispatch } from 'react-redux'

import useApi from '../hooks/rest_api'
import DataTable from '../components/data_table'
import Buttons from '../components/buttons'

function Kafka() {

    // REDUX DISPATCHER
    const dispatch = useDispatch()

    // ON LOAD..
    useEffect(() => {
        dispatch({
            type: 'menu/update',
            category: 'Kafka'
        })
    }, [])

    // FETCH KAFKA DATA FROM API
    // THEN TRANSFORM API DATA FROM JSON FORM TO ARRAY FORM
    const [api_data, ] = useApi('http://localhost:3003/kafka/', (api_response) => {
        const container = []

        // AGGREGATE THE CUMULATIVE OFFSET DELTA
        for (const topic_name in api_response) {
            let offset_delta = 0

            for (const nth in api_response[topic_name].offsets) {
                const partition = api_response[topic_name].offsets[nth]
                offset_delta += (partition.latest - partition.earliest)
            }

            // PUSH EVERYTHING TO THE CONTAINER
            container.push({
                topic_name: topic_name,
                num_partitions: api_response[topic_name].num_partitions,
                offset_delta: offset_delta
            })
        }

        return container
    })


    // CALLBACK FUNC FOR WHEN A NEW TOPIC IS CREATED IN A PROMPT
    const topic_created_cb = (api_response) => {
        console.log(api_response)
    }

    // ACTION BUTTONS UNDER TABLE
    const actions = [
        {
            label: 'Create Topic',
            icon: 'plus',
            action: () => {
                dispatch({
                    type: 'prompt/show',
                    window: 'settings',
                    callback: topic_created_cb
                })
            }
        }
    ]
    
    return (
        <div>
            <div className={ 'page_title' }>Kafka Topics</div>
            <DataTable content={ api_data } />
            <Buttons items={ actions } />
        </div>
    )
}

export default Kafka