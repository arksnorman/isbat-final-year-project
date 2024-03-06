<script setup>
import {onMounted, ref} from 'vue'
import axios from "../../axios.js"

defineProps({
  msg: String,
})

const emit = defineEmits(["reloadBlockStorage"])

const errorMessage = ref("")
const successMessage = ref("")
const creatingBlockStorage = ref(false)
const form = ref({name: "", size: 0, pool: ""})
const loadingPools = ref(false)
const pools = ref([])

async function getStoragePools() {
  loadingPools.value = true
  try {
    const res = await axios.get("/storage-pools")
    if (res.status === 200) {
      pools.value = res.data
    } else {
      errorMessage.value = "Error: " + res.statusText
    }
  } catch (e) {
    errorMessage.value = e.toString()
  }
  loadingPools.value = false
  clearMessages()
}

async function onSubmit() {
  creatingBlockStorage.value = true
  try {
    const res = await axios.post("/block-storage", form.value)
    if (res.status === 204) {
      successMessage.value = "Block storage created successfully"
      form.value = {name: "", size: 0, pool: ""}
      emit("reloadBlockStorage")
    } else {
      errorMessage.value = "Error: " + res.statusText
    }
  } catch (e) {
    errorMessage.value = e.toString()
  }
  creatingBlockStorage.value = false
  clearMessages()
}

function clearMessages() {
  setTimeout(() => {
    successMessage.value = ""
    errorMessage.value = ""
  }, 5000)
}

onMounted(async () => {
  await getStoragePools()
})

</script>


<template>
  <h4 class="mb-4">Create block storage</h4>
  <hr/>
  <div class="alert alert-danger" role="alert" v-if="errorMessage.length > 0">
    {{ errorMessage }}
  </div>
  <div class="alert alert-success" role="alert" v-if="successMessage.length > 0">
    {{ successMessage }}
  </div>
  <form @submit.prevent="onSubmit()">
    <div class="mb-3">
      <label for="pool-name" class="form-label">Name</label>
      <input v-model="form.name" type="text" class="form-control" id="pool-name">
    </div>
    <div class="mb-3">
      <label for="pool-size" class="form-label">Size in GB</label>
      <input v-model="form.size" type="text" class="form-control" id="pool-size">
    </div>
    <div class="mb-3">
      <label for="pool-block-devices" class="form-label">
        Select a storage pool
        <span class="btn" @click="getStoragePools()" title="Reload storage pools">
          <i class="fa-solid fa-arrows-rotate"></i>
        </span>
      </label>
      <div>
        <span class="spinner-border" role="status" v-if="loadingPools">
          <span class="visually-hidden">Loading...</span>
        </span>
      </div>
      <div v-if="pools.length > 0" id="pool-block-devices">
        <div class="form-check" v-for="pool in pools">
          <input
              class="form-check-input"
              type="radio"
              :value="pool.name"
              :id="pool.name"
              v-model="form.pool"
          >
          <label class="form-check-label" :for="pool.name">
            <span class="badge text-bg-dark">{{ pool.name }}</span> <span class="badge text-bg-dark">{{ pool.usedSize }}G/{{ pool.size }}G</span>
          </label>
        </div>
      </div>
      <div v-else>
        No storage pools available. Try again later
      </div>
    </div>
    <button type="submit" class="btn btn-light" :disabled="creatingBlockStorage">
      <span v-if="creatingBlockStorage" class="spinner-border spinner-border-sm" aria-hidden="true"></span>
      Create block storage
    </button>
  </form>
</template>
