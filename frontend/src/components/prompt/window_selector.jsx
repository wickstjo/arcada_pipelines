import Settings from './windows/settings'

// VALID PROMPT WINDOWS
const whitelist = {
    'settings': Settings,
}

function WindowSelector({ prompt_state }) {
    switch (prompt_state.window in whitelist) {

        case true: {
            const Selector = whitelist[prompt_state.window]
            return <Selector prompt_state={ prompt_state } />
        }

        // OTHERWISE, RENDER NOTHING
        default: { return null }
    }
}

// EXTRACT WHICH WINDOW KEYS ARE VALID
// TO PREVENT REDUCER FROM OPENING 'BAD' WINDOWS
const valid_windows = Object.keys(whitelist)

export {
    WindowSelector,
    valid_windows
}