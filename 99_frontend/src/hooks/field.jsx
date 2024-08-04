import { useState } from 'react'

const useField = (type='text') => {

    // INPUT STATE
    const [value, set_value] = useState('')

    // UPDATE
    const onChange = (event) => {
        set_value(event.target.value)
    }

    return {
        type,
        value,
        onChange
    }
}

export default useField