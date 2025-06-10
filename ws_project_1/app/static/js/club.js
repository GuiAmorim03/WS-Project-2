document.addEventListener('DOMContentLoaded', function() {
    const headers = document.querySelectorAll('.sortable');
    
    const positionOrder = {
        'GK': 1,
        'DF': 2,
        'MF': 3,
        'FW': 4
    };
    
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.column;
            const table = header.closest('table');
            const rows = Array.from(table.querySelectorAll('tbody tr'));
            
            const isAscending = header.classList.contains('ascending');
            
            headers.forEach(h => h.classList.remove('ascending', 'descending'));
            
            rows.sort((a, b) => {
                const aText = a.querySelector(`td:nth-child(${header.cellIndex + 1})`).textContent.trim();
                const bText = b.querySelector(`td:nth-child(${header.cellIndex + 1})`).textContent.trim();
                
                if (column === 'position') {
                    const aPositions = aText.split(',').map(pos => pos.trim());
                    const bPositions = bText.split(',').map(pos => pos.trim());
                    
                    const aPrimary = aPositions[0];
                    const bPrimary = bPositions[0];

                    
                    if (positionOrder[aPrimary] < positionOrder[bPrimary]) {
                        return isAscending ? 1 : -1;
                    }
                    if (positionOrder[aPrimary] > positionOrder[bPrimary]) {
                        return isAscending ? -1 : 1;
                    }
                    
                    const aSecondary = aPositions[1] || aPrimary;  
                    const bSecondary = bPositions[1] || aSecondary;  
                    
                    if (positionOrder[aSecondary] < positionOrder[bSecondary]) {
                        return isAscending ? 1 : -1;
                    }
                    if (positionOrder[aSecondary] > positionOrder[bSecondary]) {
                        return isAscending ? -1 : 1;
                    }
                    return 0;
                } else {
                    
                    const aValue = isNaN(aText) ? aText : parseFloat(aText);
                    const bValue = isNaN(bText) ? bText : parseFloat(bText);

                    if (aValue < bValue) return isAscending ? 1 : -1;
                    if (aValue > bValue) return isAscending ? -1 : 1;
                    return 0;
                }
            });

            rows.forEach(row => table.querySelector('tbody').appendChild(row));

            header.classList.toggle('ascending', !isAscending);
            header.classList.toggle('descending', isAscending);
        });
    });
    
    // Add loading indicator for club navigation
    window.addEventListener('beforeunload', function() {
        // Show loading state when navigating away
        const body = document.body;
        if (body) {
            body.style.opacity = '0.7';
            body.style.pointerEvents = 'none';
        }
    });
});
