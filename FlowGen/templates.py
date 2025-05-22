# Predefined templates for FlowGen

TEMPLATES = {
    'Project Management Flow': {
        'nodes': [
            {'type': 'rectangle', 'x': 50, 'y': 50, 'text': 'Start', 'color': '#A0C4FF'},
            {'type': 'rectangle', 'x': 200, 'y': 50, 'text': 'Planning', 'color': '#BDB2FF'},
            {'type': 'rectangle', 'x': 350, 'y': 50, 'text': 'Execution', 'color': '#FFC6FF'},
            {'type': 'rectangle', 'x': 500, 'y': 50, 'text': 'Closure', 'color': '#FFADAD'},
        ],
        'connections': [
            {'from': '0', 'to': '1'},
            {'from': '1', 'to': '2'},
            {'from': '2', 'to': '3'},
        ]
    },
    'Decision Tree': {
        'nodes': [
            {'type': 'diamond', 'x': 200, 'y': 200, 'text': 'Decision?', 'color': '#FFD6A5'},
            {'type': 'rectangle', 'x': 100, 'y': 350, 'text': 'Option A', 'color': '#FDFFB6'},
            {'type': 'rectangle', 'x': 300, 'y': 350, 'text': 'Option B', 'color': '#FDFFB6'},
        ],
        'connections': [
            {'from': '0', 'to': '1'},
            {'from': '0', 'to': '2'},
        ]
    }
}
