<script setup>
import { ref, onMounted } from 'vue'
import { getRecommendations } from '../api/recommendations'

const data = ref(null)
const loading = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    data.value = await getRecommendations(24)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load recommendations.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="rec-view">
    <div class="header-row">
      <h1>Recommended for You</h1>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="muted">Loading…</p>

    <div v-else-if="data" class="content">
      <!-- Case 1: not enough ratings -->
      <div v-if="data.message" class="notice">
        <p>{{ data.message }}</p>
        <router-link to="/movies" class="btn-link"> Go to Catalog → </router-link>
      </div>

      <!-- Case 2: has recommendations -->
      <template v-else>
        <div class="genre-summary">
          <span class="label">Based on your taste in:</span>
          <span v-for="g in data.top_genres" :key="g" class="genre-badge">
            {{ g }}
          </span>
        </div>

        <p v-if="data.recommendations.length === 0" class="muted">
          No recommendations yet. Try rating more movies.
        </p>

        <div v-else class="grid">
          <div v-for="movie in data.recommendations" :key="movie.id" class="card">
            <div class="card-head">
              <h3>{{ movie.title }}</h3>
              <span v-if="movie.external_rating" class="rating">
                IMDb {{ movie.external_rating }}
              </span>
            </div>
            <p class="desc">{{ movie.description }}</p>
            <div class="card-foot">
              <span class="genre">{{ movie.genre }}</span>
              <router-link :to="{ name: 'movies' }" class="btn-link-small">
                Open in catalog →
              </router-link>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.rec-view {
  max-width: 1200px;
  margin: 0 auto;
}
.header-row {
  margin-bottom: 1.5rem;
}
h1 {
  margin: 0;
}
.content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.genre-summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.8rem 1rem;
}
.label {
  color: #94a3b8;
  font-size: 0.85rem;
  margin-right: 0.3rem;
}
.genre-badge {
  background: #1e40af33;
  color: #93c5fd;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.8rem;
}
.notice {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
}
.notice p {
  color: #cbd5e1;
  margin: 0 0 1rem 0;
}
.btn-link {
  color: #60a5fa;
  text-decoration: none;
  font-size: 0.9rem;
}
.btn-link:hover {
  text-decoration: underline;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}
.card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: start;
  gap: 0.5rem;
}
.card-head h3 {
  margin: 0;
  font-size: 1rem;
}
.rating {
  color: #fbbf24;
  font-size: 0.8rem;
  white-space: nowrap;
}
.desc {
  color: #94a3b8;
  font-size: 0.85rem;
  margin: 0;
  flex: 1;
}
.card-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.genre {
  background: #1e40af33;
  color: #93c5fd;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}
.btn-link-small {
  color: #60a5fa;
  text-decoration: none;
  font-size: 0.8rem;
}
.btn-link-small:hover {
  text-decoration: underline;
}
.muted {
  color: #94a3b8;
  text-align: center;
  font-size: 0.9rem;
}
.error {
  color: #f87171;
  padding: 0.6rem;
  background: #7f1d1d33;
  border-radius: 6px;
}
</style>
