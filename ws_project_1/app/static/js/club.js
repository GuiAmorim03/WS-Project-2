document.addEventListener('DOMContentLoaded', function() {
    const headers = document.querySelectorAll('.sortable');
    
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.column;  // Pega o nome da coluna para ordenar
            const table = header.closest('table');  // A tabela que contém o cabeçalho
            const rows = Array.from(table.querySelectorAll('tbody tr')); // Todas as linhas da tabela
            
            // Descobre se a coluna já está ordenada
            const isAscending = header.classList.contains('ascending');
            
            // Remove qualquer ordenação existente
            headers.forEach(h => h.classList.remove('ascending', 'descending'));
            
            rows.sort((a, b) => {
                const aText = a.querySelector(`td:nth-child(${header.cellIndex + 1})`).textContent.trim();
                const bText = b.querySelector(`td:nth-child(${header.cellIndex + 1})`).textContent.trim();

                // Convertendo os dados para números ou strings conforme necessário
                const aValue = isNaN(aText) ? aText : parseFloat(aText);
                const bValue = isNaN(bText) ? bText : parseFloat(bText);

                if (aValue < bValue) return isAscending ? 1 : -1;
                if (aValue > bValue) return isAscending ? -1 : 1;
                return 0;
            });

            // Adiciona as linhas ordenadas de volta à tabela
            rows.forEach(row => table.querySelector('tbody').appendChild(row));

            // Adiciona a classe de ordenação para a coluna clicada
            header.classList.toggle('ascending', !isAscending);
            header.classList.toggle('descending', isAscending);
        });
    });
});
