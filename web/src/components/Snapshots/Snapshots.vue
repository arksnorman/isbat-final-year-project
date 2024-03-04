<script setup>
import {onMounted, ref} from 'vue'
import axios from "../../axios.js"

defineProps({
  msg: String,
})

const blockDevices = ref([])
const loadingBlockStorage = ref(false)
const errorMessage = ref("")
const successMessage = ref("")
const isDeletingSnapshot = ref(false)
const snapshotToBeDeleted = ref("")
const snapshotToBeRestored = ref("")
const form = ref({blockDevice: ""})
const isLoadingSnapshots = ref(false)
const snapshots = ref([])
const isRestoringSnapshot = ref(false)
const blockDeviceAndPoolInfo = ref ({pool: "", device: "", snapshot: ""})

async function getBlockStorage() {
  loadingBlockStorage.value = true
  try {
    const res = await axios.get("/block-storage")
    if (res.status === 200) {
      blockDevices.value = res.data
    } else {
      errorMessage.value = "Error: " + res.statusText
    }
  } catch (e) {
    errorMessage.value = e.toString()
  }
  loadingBlockStorage.value = false
  clearMessages()
}

async function loadSnapshots() {
  if (form.value.blockDevice.length === 0) {
    errorMessage.value = "You need to select a block storage device"
    return
  }
  isLoadingSnapshots.value = true
  getBlockData(form.value.blockDevice)
  try {
    const res = await axios.get("/snapshots", {params: form.value})
    if (res.status === 200) {
      snapshots.value = res.data
    } else {
      errorMessage.value = "Error: " + res.statusText
    }
  } catch (e) {
    errorMessage.value = e.toString()
  }
  isLoadingSnapshots.value = false
  clearMessages()
}


function getBlockData(device) {
  blockDevices.value.forEach((blockDevice) => {
    blockDeviceAndPoolInfo.value.pool = blockDevice.pool
    blockDeviceAndPoolInfo.value.device = blockDevice.name
  })
  console.log(blockDeviceAndPoolInfo.value)
}

async function restoreSnapshot(snapshot) {
  snapshotToBeRestored.value = snapshot
  isRestoringSnapshot.value = true
  try {
    blockDeviceAndPoolInfo.value.snapshot = snapshot
    const res = await axios.put("/snapshots", blockDeviceAndPoolInfo.value)
    if (res.status === 204) {
      successMessage.value = "Snapshot restored successfully"
      await loadSnapshots()
    } else {
      errorMessage.value = "Error: " + res.statusText
    }
  } catch (e) {
    errorMessage.value = e.toString()
  }
  isRestoringSnapshot.value = false
  clearMessages()
}

async function deleteSnapshot(snapshot) {
  if (!confirm("Are you sure you want to proceed with action?")) {
    return
  }
  snapshotToBeDeleted.value = snapshot
  isDeletingSnapshot.value = true
  blockDeviceAndPoolInfo.value.device = snapshot
  try {
    const res = await axios.delete("/snapshots", {data: blockDeviceAndPoolInfo.value})
    if (res.status === 204) {
      successMessage.value = "Snapshot deleted successfully"
      await loadSnapshots()
    } else {
      errorMessage.value = "Error: " + res.statusText
    }
  } catch (e) {
    errorMessage.value = e.toString()
  }
  isDeletingSnapshot.value = false
  clearMessages()
}

onMounted(async () => {
  await getBlockStorage()
})


function clearMessages() {
  setTimeout(() => {
    successMessage.value = ""
    errorMessage.value = ""
  }, 5000)
}

</script>



<template>
  <div class="row">
    <div class="col-12">
      <div class="row">
        <div class="col-6">
          <h4>
            <i class="fa-solid fa-copy"></i>
            Block Storage Snapshots
          </h4>
        </div>
        <div class="col-6 text-end">
          <div class="row g-3 justify-content-end">
            <div class="col-auto">
              <label for="block-devices" class="col-form-label">Select block storage device</label>
            </div>
            <div class="col-auto">
              <div class="spinner-border" role="status" v-if="loadingBlockStorage">
                <span class="visually-hidden">Loading snapshots. Please wait...</span>
              </div>
              <select class="form-select" v-model="form.blockDevice" v-else>
                <option
                  v-for="blockDevice in blockDevices"
                  :value="blockDevice.name"
                >
                  {{ blockDevice.name }}
                </option>
              </select>
            </div>
            <div class="col-auto">
              <button @click="loadSnapshots()" class="btn btn-light float-end" :disabled="isLoadingSnapshots">
                <span v-if="isLoadingSnapshots" class="spinner-border spinner-border-sm" aria-hidden="true"></span>
                Load snapshots
              </button>
            </div>
          </div>
        </div>
      </div>

      <hr/>
      <div class="alert alert-danger" role="alert" v-if="errorMessage.length > 0">
        {{ errorMessage }}
      </div>
      <div class="alert alert-success" role="alert" v-if="successMessage.length > 0">
        {{ successMessage }}
      </div>
      <div class="spinner-border" role="status" v-if="isLoadingSnapshots">
        <span class="visually-hidden">Loading snapshots. Please wait...</span>
      </div>
      <div v-if="snapshots.length === 0">
        No snapshots available for block storage {{ form.blockDevice }}
      </div>
      <div class="table-responsive" v-else>
        <table class="table table-borderless">
          <thead>
          <tr>
            <th scope="col">Snapshot ID</th>
            <th scope="col">Block Storage Device</th>
            <th scope="col">Time Taken</th>
            <th scope="col">Size</th>
            <th scope="col">Status</th>
            <th scope="col">&nbsp;</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="snapshot in snapshots">
            <th scope="row">
              <i class="fa-solid fa-copy"></i>
              {{ snapshot.name }}
            </th>
            <td>
              <i class="fa-regular fa-hard-drive"></i>
              {{ snapshot.origin }}
            </td>
            <td>
              <i class="fa-regular fa-hard-drive"></i>
              {{ snapshot.time }}
            </td>
            <td><span class="badge text-bg-dark">{{ snapshot.size }}G</span></td>
            <td class="text-success"><i class="fa-regular fa-circle-check"></i> Available</td>
            <td class="text-end">
              <span
                v-if="snapshotToBeRestored === snapshot.name && isRestoringSnapshot"
                class="spinner-border text-secondary spinner-border-sm"
                aria-hidden="true"
              >
              </span>
              <span
                v-else
                @click="restoreSnapshot(snapshot.name)"
                title="Restore snapshot"
                class="text-secondary"
              >
                <i class="fa-solid fa-rotate-right"></i>
              </span>

              <span
                v-if="snapshotToBeDeleted === snapshot.name && isDeletingSnapshot"
                class="spinner-border text-danger spinner-border-sm ms-2"
                aria-hidden="true"
              >
              </span>
              <span
                v-else
                @click="deleteSnapshot(snapshot.name)"
                class="fa-regular fa-trash-can ms-2 text-danger"
                title="Delete block storage"
              >
              </span>

            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
