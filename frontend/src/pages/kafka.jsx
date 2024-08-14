import { useEffect } from 'react'
import { useDispatch } from 'react-redux'

import useApi from '../hooks/rest_api'
import DataTable from '../components/data_table'

function Kafka() {

    // REDUX DISPATCHER
    const dispatch = useDispatch()

    const [api_data, api_funcs] = useApi('http://localhost:3003/kafka/')
    // console.log(api_data)

    // ON LOAD..
    useEffect(() => {
        dispatch({
            type: 'menu/update',
            category: 'Kafka'
        })
    })
    
    return (
        <div>
            <div className={ 'page_title' }>Kafka Topics</div>
            <DataTable content={[
                {
                    topic_name: 'foo',
                    n_partitions: 3,
                    offset_delta: 164
                },
                {
                    topic_name: 'bar',
                    n_partitions: 1,
                    offset_delta: 87
                },
                {
                    topic_name: 'biz',
                    n_partitions: 5,
                    offset_delta: 13
                }
            ]} />
        </div>
    )
}

export default Kafka