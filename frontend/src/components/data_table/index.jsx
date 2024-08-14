import './styles.scss'

function DataTable({ content }) { return (
    <div className={ 'data_table' }>
        <div className={ 'headers' }>
            { Object.keys(content[0]).map(item =>
                <div className={ 'column' } key={ item }>{ item }</div>
            )}
        </div>
        { content.map((item, index) =>
            <div className={ 'row' } key={ item + index }>
                { Object.values(item).map((value, index) =>
                    <div className={ 'column' } key={ index + value }>{ value }</div>
                )}
            </div>
        )}
    </div>
)}

export default DataTable