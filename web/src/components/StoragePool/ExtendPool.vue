<script setup>
import {onMounted, ref} from 'vue'
import axios from "../../axios.js"

const props = defineProps({
  poolName: String,
})

const emit = defineEmits(["reloadPools"])

const blockDevices = ref([])
const loadingBlockDevices = ref(false)
const errorMessage = ref("")
const successMessage = ref("")
const extendingPool = ref(false)
const form = ref({name: "", blockDevices: []})

form.value.name = props.poolName

async function getBlockDevices() {
  blockDevices.value = []
  loadingBlockDevices.value = true
  try {
    const res = await axios.get("/block-devices")
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
  extendingPool.value = true
  try {
    const res = await axios.put("/storage-pools", form.value)
    if (res.status === 204) {
      successMessage.value = "Storage pool extended successfully"
      form.value = {name: "", blockDevices: []}
      emit("reloadPools")
    } else {
      errorMessage.value = "Error: " + res.statusText
    }
  } catch (e) {
    errorMessage.value = e.toString()
  }
  extendingPool.value = false
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
  <h4 class="mb-4">Extend pool storage</h4>
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
      <input v-model="form.name" type="text" class="form-control" id="pool-name" disabled>
    </div>
    <div class="mb-3">
      <label for="pool-block-devices" class="form-label">
        Select block devices
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
        No block devices available. Try again later
      </div>
    </div>
    <button type="submit" class="btn btn-light" :disabled="extendingPool">
      <span v-if="extendingPool" class="spinner-border spinner-border-sm" aria-hidden="true"></span>
      Extend storage pool
    </button>
  </form>
</template>
