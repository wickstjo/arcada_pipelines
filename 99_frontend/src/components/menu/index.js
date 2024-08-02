import './styles.css'
import { useState, useEffect } from 'react'

function Container() {

    // RESOURCE STATE
    const [local, set_local] = useState([])

    // ON LOAD, LOAD RESOURCE
    useEffect(() => {
        console.log('FOO')
    }, [])

    return (
        <div className="main_menu">
            Foo
        </div>
    )
}

export default Container;