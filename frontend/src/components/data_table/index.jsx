import './styles.scss'

function DataTable({ content }) {
    switch (content.length > 0) {

        // ITEMS FOUND, RENDER THEM
        case true: { return (
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

        // OTHERWISE, RENDER PSEUDO ERROR
        default: { return (
            <div className={ 'data_table' }>
                <div className={ 'row' }>
                    <div className={ 'column' }>No items found.</div>
                </div>
            </div>
        )}
    }
}

export default DataTable