<script setup>
import { ref, onMounted, computed } from 'vue'
import {
  listSchedules,
  createSchedule,
  updateScheduleStatus,
  deleteSchedule,
} from '../api/schedule'
import { listMovies } from '../api/movies'

const schedules = ref([])
const movies = ref([])
const loading = ref(false)
const error = ref('')
const filterStatus = ref('')

const showForm = ref(false)
const selectedMovieId = ref('')
const scheduledDate = ref('')

const today = computed(() => new Date().toISOString().slice(0, 10))

async function loadSchedules() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filterStatus.value) params.status = filterStatus.value
    schedules.value = await listSchedules(params)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load schedules.'
  } finally {
    loading.value = false
  }
}

async function loadMovies() {
  try {
    movies.value = await listMovies({ limit: 100 })
  } catch (e) {
    // ignore
  }
}

async function handleCreate() {
  if (!selectedMovieId.value || !scheduledDate.value) return
  error.value = ''
  try {
    await createSchedule(Number(selectedMovieId.value), scheduledDate.value)
    showForm.value = false
    selectedMovieId.value = ''
    scheduledDate.value = ''
    await loadSchedules()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to create schedule.'
  }
}

async function handleStatusChange(schedule, newStatus) {
  try {
    await updateScheduleStatus(schedule.id, newStatus)
    await loadSchedules()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to update status.'
  }
}

async function handleDelete(schedule) {
  if (!confirm('Delete this schedule?')) return
  try {
    await deleteSchedule(schedule.id)
    await loadSchedules()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to delete schedule.'
  }
}

function applyFilter() {
  loadSchedules()
}

function formatDate(d) {
  return new Date(d + 'T00:00:00').toLocaleDateString()
}

onMounted(() => {
  loadSchedules()
  loadMovies()
})
</script>

<template>
  <div class="schedule-view">
    <div class="header-row">
      <h1>My Schedule</h1>
      <button class="btn-primary" @click="showForm = !showForm">
        {{ showForm ? 'Cancel' : '+ Schedule a Movie' }}
      </button>
    </div>

    <form v-if="showForm" class="schedule-form" @submit.prevent="handleCreate">
      <label>
        Movie
        <select v-model="selectedMovieId" required>
          <option value="" disabled>Select a movie…</option>
          <option v-for="m in movies" :key="m.id" :value="m.id">
            {{ m.title }} ({{ m.genre }})
          </option>
        </select>
      </label>
      <label>
        Date
        <input v-model="scheduledDate" type="date" :min="today" required />
      </label>
      <button type="submit" class="btn-primary">Create</button>
    </form>

    <div class="filters">
      <label>
        Status
        <select v-model="filterStatus" @change="applyFilter">
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="done">Done</option>
          <option value="missed">Missed</option>
        </select>
      </label>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="muted">Loading…</p>
    <p v-else-if="schedules.length === 0" class="muted">No schedules yet.</p>

    <ul v-else class="schedule-list">
      <li v-for="s in schedules" :key="s.id" :class="['schedule-item', 'status-' + s.status]">
        <div class="schedule-info">
          <h3>{{ s.movie.title }}</h3>
          <p class="meta">
            <span class="genre">{{ s.movie.genre }}</span>
            <span class="date">📅 {{ formatDate(s.scheduled_date) }}</span>
            <span :class="['status-badge', s.status]">{{ s.status }}</span>
          </p>
        </div>
        <div class="schedule-actions">
          <button
            v-if="s.status !== 'done'"
            class="btn-secondary"
            @click="handleStatusChange(s, 'done')"
          >
            Mark done
          </button>
          <button
            v-if="s.status === 'pending'"
            class="btn-secondary"
            @click="handleStatusChange(s, 'missed')"
          >
            Missed
          </button>
          <button class="btn-danger" @click="handleDelete(s)">Delete</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.schedule-view {
  max-width: 900px;
  margin: 0 auto;
}
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
h1 {
  margin: 0;
}
.btn-primary {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.6rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-primary:hover {
  background: #2563eb;
}
.btn-secondary {
  background: #334155;
  color: #e2e8f0;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
}
.btn-secondary:hover {
  background: #475569;
}
.btn-danger {
  background: transparent;
  color: #f87171;
  border: 1px solid #7f1d1d;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
}
.btn-danger:hover {
  background: #7f1d1d33;
}
.schedule-form {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 1.2rem;
  margin-bottom: 1.5rem;
  display: grid;
  grid-template-columns: 2fr 1fr auto;
  gap: 1rem;
  align-items: end;
}
.schedule-form label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: #cbd5e1;
}
.schedule-form select,
.schedule-form input {
  padding: 0.5rem 0.7rem;
  border-radius: 6px;
  border: 1px solid #475569;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 0.9rem;
}
.schedule-form select:focus,
.schedule-form input:focus {
  outline: none;
  border-color: #3b82f6;
}
.filters {
  margin-bottom: 1.2rem;
}
.filters label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #94a3b8;
}
.filters select {
  padding: 0.4rem 0.7rem;
  border-radius: 6px;
  border: 1px solid #475569;
  background: #0f172a;
  color: #e2e8f0;
}
.schedule-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}
.schedule-item {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 1rem 1.2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.schedule-item.status-done {
  opacity: 0.65;
}
.schedule-info h3 {
  margin: 0 0 0.4rem 0;
  font-size: 1rem;
}
.meta {
  display: flex;
  gap: 0.8rem;
  align-items: center;
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
  flex-wrap: wrap;
}
.genre {
  background: #1e40af33;
  color: #93c5fd;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}
.status-badge {
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.status-badge.pending {
  background: #f59e0b33;
  color: #fbbf24;
}
.status-badge.done {
  background: #10b98133;
  color: #34d399;
}
.status-badge.missed {
  background: #ef444433;
  color: #f87171;
}
.schedule-actions {
  display: flex;
  gap: 0.5rem;
}
.muted {
  color: #94a3b8;
  text-align: center;
  padding: 2rem;
}
.error {
  color: #f87171;
  padding: 0.6rem;
  background: #7f1d1d33;
  border-radius: 6px;
}
</style>
