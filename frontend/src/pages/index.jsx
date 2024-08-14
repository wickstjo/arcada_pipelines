import { Routes, Route, Navigate } from 'react-router-dom'

import Models from './models'
import Actions from './actions'
import Kafka from './kafka'
import Cassandra from './cassandra'
import NotFound from './not_found'

function Pages() { return (
    <Routes>
        <Route exact path={ '/' } element={ <Navigate replace to={ '/models' } /> } />
        <Route exact path={ '/models' } element={ <Models /> } />
        <Route exact path={ '/actions' } element={ <Actions /> } />

        <Route exact path={ '/kafka' } element={ <Kafka /> } />
        <Route exact path={ '/cassandra' } element={ <Cassandra /> } />

        {/* <Route path={ '/blogs/:id' } element={ <Blog /> } />

        <Route exact path={ '/users' } element={ <Users /> } />
        <Route path={ '/users/:id' } element={ <User /> } /> */}

        <Route path={ '/*' } element={ <NotFound /> } />
    </Routes>
)}

export default Pages