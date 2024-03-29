<script setup>
import {onMounted, ref} from 'vue'
import axios from "../../axios.js"

defineProps({
  msg: String,
})

const emit = defineEmits(["reloadPools"])

const blockDevices = ref([])
const loadingBlockDevices = ref(false)
const errorMessage = ref("")
const successMessage = ref("")
const creatingStoragePool = ref(false)
const form = ref({name: "", blockDevices: []})

async function getBlockDevices() {
  blockDevices.value = []
  loadingBlockDevices.value = true
  try {
    const res = await axios.get("/physical-devices")
    if (res.status === 200) {
      blockDevices.value = res.data
    } else {
      errorMessage.value = "Error: " + res.statusText
    }
  } catch (e) {
    errorMessage.value = e.toString()
  }
  loadingBlockDevices.value = false
  clearMessages()
}

async function onSubmit() {
  creatingStoragePool.value = true
  try {
    const res = await axios.post("/storage-pools", form.value)
    if (res.status === 204) {
      successMessage.value = "Storage pool created successfully"
      form.value = {name: "", blockDevices: []}
      emit("reloadPools")
      await getBlockDevices()
    } else {
      errorMessage.value = "Error: " + res.statusText
    }
  } catch (e) {
    errorMessage.value = e.toString()
  }
  creatingStoragePool.value = false
  clearMessages()
}

function clearMessages() {
  setTimeout(() => {
    successMessage.value = ""
    errorMessage.value = ""
  }, 5000)
}

onMounted(async () => {
  await getBlockDevices()
})

</script>


<template>
  <h4 class="mb-4">Create a new storage pool</h4>
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
      <label for="pool-block-devices" class="form-label">
        Select physical devices
        <span class="btn" @click="getBlockDevices()" title="Reload block devices">
          <i class="fa-solid fa-arrows-rotate"></i>
        </span>
      </label>
      <div>
        <span class="spinner-border" role="status" v-if="loadingBlockDevices">
          <span class="visually-hidden">Loading...</span>
        </span>
      </div>
      <div v-if="blockDevices.length > 0" id="pool-block-devices">
        <div class="form-check" v-for="blockDevice in blockDevices">
          <input
            class="form-check-input"
            type="checkbox"
            :value="blockDevice.device"
            :id="blockDevice.device"
            v-model="form.blockDevices"
          >
          <label class="form-check-label" :for="blockDevice.device">
            <span class="badge text-bg-dark">{{ blockDevice.device }}</span> <span class="badge text-bg-dark">{{ blockDevice.size }}</span>
          </label>
        </div>
      </div>
      <div v-else>
        No physical devices available. Try again later
      </div>
    </div>
    <button type="submit" class="btn btn-light" :disabled="creatingStoragePool">
      <span v-if="creatingStoragePool" class="spinner-border spinner-border-sm" aria-hidden="true"></span>
      Create storage pool
    </button>
  </form>
</template>
