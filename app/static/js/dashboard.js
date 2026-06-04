document.addEventListener('DOMContentLoaded', () => {
    loadTasks();

    // Envio do formulário do modal
    document.getElementById('task-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const titulo = document.getElementById('task-title').value;
        const dia_semana = document.getElementById('task-day').value;
        const horario = document.getElementById('task-time').value; // Retorna "HH:MM"

        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ titulo, dia_semana, horario })
        });

        if (response.ok) {
            document.getElementById('task-form').reset();
            const modal = bootstrap.Modal.getInstance(document.getElementById('taskModal'));
            modal.hide();
            loadTasks(); // Recarrega aplicando a nova expansão se houver
        } else {
            alert('Erro ao salvar tarefa.');
        }
    });
});

async function loadTasks() {
    const response = await fetch('/api/tasks');
    if (!response.ok) return;
    const tasks = await response.json();

    // 1. Define os limites padrão exigidos (06 AM às 22 PM)
    let startHour = 6;
    let endHour = 22;

    // 2. Inteligência Dinâmica: Verifica se alguma task extrapola o limite padrão
    tasks.forEach(task => {
        const taskHour = parseInt(task.horario.split(':')[0]);
        if (taskHour < startHour) startHour = taskHour;
        if (taskHour > endHour) endHour = taskHour;
    });

    // 3. Renderiza as linhas do Grid com base no range calculado
    renderGrid(startHour, endHour);

    // 4. Injeta as tarefas nas respectivas células geradas
    tasks.forEach(task => {
        // Formata o horário da task para bater com o ID da linha (ex: "08:00")
        const formattedHour = task.horario.split(':')[0].padStart(2, '0') + ':00';
        const cellId = `cell-${task.dia_semana}-${formattedHour}`;
        const cell = document.getElementById(cellId);
        
        if (cell) {
            const badge = document.createElement('div');
            badge.className = 'task-badge mb-1';
            // Mostra o horário exato inserido pelo usuário ao lado do título
            badge.innerText = `[${task.horario}] ${task.titulo}`;
            cell.appendChild(badge);
        }
    });
}

function renderGrid(start, end) {
    const tbody = document.getElementById('calendar-body');
    tbody.innerHTML = ''; // Limpa a tabela anterior

    const dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];

    // Cria as linhas de hora em hora
    for (let h = start; h <= end; h++) {
        const horaFormatada = String(h).padStart(2, '0') + ':00';
        
        const tr = document.createElement('tr');
        
        // Coluna do Horário
        const tdHora = document.createElement('td');
        tdHora.className = 'fw-bold text-secondary text-muted small';
        tdHora.innerText = horaFormatada;
        tr.appendChild(tdHora);

        // Colunas dos Dias da Semana
        dias.forEach(dia => {
            const tdDia = document.createElement('td');
            tdDia.id = `cell-${dia}-${horaFormatada}`;
            tdDia.className = 'grid-cell';
            tr.appendChild(tdDia);
        });

        tbody.appendChild(tr);
    }
}