// Variável global para guardar temporariamente os dados da task ativa no modal
let activeTaskData = null;

document.addEventListener('DOMContentLoaded', () => {
    loadTasks();

    // Mapeia o clique do botão Nova Tarefa limpando o modal de forma segura
    const btnNovaTarefa = document.querySelector('[data-bs-target="#taskModal"]');
    if (btnNovaTarefa) {
        btnNovaTarefa.addEventListener('click', () => {
            const form = document.getElementById('task-form');
            if (form) form.reset();
            
            const title = document.querySelector('.modal-title');
            if (title) title.innerText = "Registrar na Grade";
            
            const btnSubmit = document.getElementById('btn-submit-task');
            if (btnSubmit) { btnSubmit.style.display = "inline-block"; btnSubmit.innerText = "Salvar na Grade"; }
            
            const btnDelete = document.getElementById('btn-delete-task');
            if (btnDelete) btnDelete.style.display = "none";
            
            document.getElementById('task-title').disabled = false;
            document.getElementById('task-day').disabled = false;
            document.getElementById('task-time').disabled = false;
            activeTaskData = null;
        });
    }

    // Envio do formulário do modal (Criação ou Edição)
    const taskForm = document.getElementById('task-form');
    if (taskForm) {
        taskForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const titulo = document.getElementById('task-title').value;
            const dia_semana = document.getElementById('task-day').value;
            const horario = document.getElementById('task-time').value;

            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ titulo, dia_semana, horario })
            });

            if (response.ok) {
                fecharModal();
                // Limpa os badges antes de recarregar
                document.querySelectorAll('.task-badge').forEach(b => b.remove());
                loadTasks();
            } else {
                alert('Erro ao salvar tarefa.');
            }
        });
    }

    // --- ESCUTA O CLIQUE DE EXCLUSÃO DE FORMA DIRETA E SEGURA ---
    const btnDeleteTask = document.getElementById('btn-delete-task');
    if (btnDeleteTask) {
        console.log("✅ O JavaScript encontrou o botão de excluir e ativou o monitoramento!");
        
        btnDeleteTask.addEventListener('click', async () => {
            console.log("🚨 Botão Excluir clicado! Dados da task ativa:", activeTaskData);
            
            if (!activeTaskData) {
                console.log("❌ Erro: activeTaskData está vazio ou nulo!");
                return;
            }
            
            if (confirm(`Tem certeza que deseja excluir a tarefa "${activeTaskData.titulo}"?`)) {
                console.log("📡 Disparando requisição DELETE para /api/tasks...");
                
                const response = await fetch('/api/tasks', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(activeTaskData)
                });

                console.log("📥 Resposta do servidor recebida. Status:", response.status);

                if (response.ok) {
                    fecharModal();
                    // Remove os badges antigos do grid antes de atualizar
                    document.querySelectorAll('.task-badge').forEach(badge => badge.remove());
                    loadTasks();
                    console.log("🎉 Grade atualizada com sucesso!");
                } else {
                    alert('Erro ao excluir tarefa.');
                }
            }
        });
    } else {
        console.log("❌ Elemento 'btn-delete-task' não foi mapeado.");
    }
});

async function loadTasks() {
    const response = await fetch('/api/tasks');
    if (!response.ok) return;
    const tasks = await response.json();

    let startHour = 6;
    let endHour = 22;

    tasks.forEach(task => {
        const taskHour = parseInt(task.horario.split(':')[0]);
        if (taskHour < startHour) startHour = taskHour;
        if (taskHour > endHour) endHour = taskHour;
    });

    renderGrid(startHour, endHour);

    // Injeta as tarefas nas respectivas células geradas com base na hora inteira
    tasks.forEach(task => {
        const horaCheia = task.horario.split(':')[0].padStart(2, '0') + ':00';
        const cellId = `cell-${task.dia_semana}-${horaCheia}`;
        const cell = document.getElementById(cellId);
        
        if (cell) {
            const badge = document.createElement('div');
            badge.className = 'task-badge mb-1';
            badge.style.cursor = 'pointer'; // Aplica a mãozinha de botão
            badge.innerText = `[${task.horario}] ${task.titulo}`;
            
            // Evento de clique dinâmico
            badge.addEventListener('click', (e) => {
                e.stopPropagation();
                abrirModalVisualizacao(task);
            });

            cell.appendChild(badge);
        }
    });
}

function renderGrid(start, end) {
    const tbody = document.getElementById('calendar-body');
    if (!tbody) return;
    tbody.innerHTML = '';
    const dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];

    for (let h = start; h <= end; h++) {
        const horaFormatada = String(h).padStart(2, '0') + ':00';
        const tr = document.createElement('tr');
        
        const tdHora = document.createElement('td');
        tdHora.className = 'fw-bold text-secondary text-muted small';
        tdHora.innerText = horaFormatada;
        tr.appendChild(tdHora);

        dias.forEach(dia => {
            const tdDia = document.createElement('td');
            tdDia.id = `cell-${dia}-${horaFormatada}`;
            tdDia.className = 'grid-cell';
            tr.appendChild(tdDia);
        });

        tbody.appendChild(tr);
    }
}

function abrirModalVisualizacao(task) {
    activeTaskData = task;
    
    const modalTitle = document.querySelector('.modal-title');
    if (modalTitle) modalTitle.innerText = "Detalhes / Editar Tarefa";
    
    const inputTitle = document.getElementById('task-title');
    const inputDay = document.getElementById('task-day');
    const inputTime = document.getElementById('task-time');
    
    if (inputTitle) { inputTitle.value = task.titulo; inputTitle.disabled = false; }
    if (inputDay) { inputDay.value = task.dia_semana; inputDay.disabled = false; }
    if (inputTime) { inputTime.value = task.horario; inputTime.disabled = false; }

    const btnSubmit = document.getElementById('btn-submit-task');
    const btnDelete = document.getElementById('btn-delete-task');
    const btnCancel = document.getElementById('btn-cancel-task');
    
    if (btnSubmit) { btnSubmit.style.display = "inline-block"; btnSubmit.innerText = "Salvar Alterações"; }
    if (btnDelete) {
        btnDelete.style.setProperty('display', 'inline-block', 'important'); // Força a exibição acima de tudo
        btnDelete.removeAttribute('disabled');
    } if (btnCancel) btnCancel.innerText = "Cancelar";

    const modalElement = document.getElementById('taskModal');
    if (modalElement) {
        let modal = bootstrap.Modal.getInstance(modalElement);
        if (!modal) {
            modal = new bootstrap.Modal(modalElement);
        }
        modal.show();
    }
}

function fecharModal() {
    const modalElement = document.getElementById('taskModal');
    if (modalElement) {
        const btnFechar = modalElement.querySelector('.btn-close') || document.getElementById('btn-cancel-task');
        if (btnFechar) {
            btnFechar.click();
        } else {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) modal.hide();
        }
    }
    
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) backdrop.remove();
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
}