<script setup>
import {onMounted, ref} from 'vue'
import axios from "../../axios.js"
import CreateBlockStorage from "./CreateBlockStorage.vue";

defineProps({
  msg: String,
})

const blockDevices = ref([])
const loadingBlockStorage = ref(false)
const errorMessage = ref("")
const successMessage = ref("")
const createNewBlockStorage = ref(false)
const isDeletingBlockStorage = ref(false)
const deviceToBeDeleted = ref("")
const isCreatingSnapshot = ref(false)
const snapshotDevice = ref("")

async function takeSnapshot(pool, device) {
  snapshotDevice.value = device
  isCreatingSnapshot.value = true
  try {
    const data = {pool: pool, device: device}
    const res = await axios.post("/snapshots", data)
    if (res.status === 204) {
      snapshotDevice.value = ""
      successMessage.value = "Snapshot is now available"
    } else {
      errorMessage.value = "Error: " + res.statusText
    }
  } catch (e) {
    errorMessage.value = e.toString()
  }
  isCreatingSnapshot.value = false
  clearMessages()
}

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

async function deleteBlockStorage(pool, blockDevice) {
  if (!confirm("Are you sure you want to proceed with action?")) {
    return
  }
  deviceToBeDeleted.value = blockDevice
  isDeletingBlockStorage.value = true
  try {
    const data = {storagePool: pool, blockDevice: blockDevice}
    const res = await axios.delete("/block-storage", {data: data})
    if (res.status === 204) {
      successMessage.value = "Block storage deleted successfully"
      await getBlockStorage()
    } else {
      errorMessage.value = "Error: " + res.statusText
    }
  } catch (e) {
    errorMessage.value = e.toString()
  }
  isDeletingBlockStorage.value = false
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
    <div class="col-8">
      <div class="row">
        <div class="col-7">
          <h4>
            <i class="fa-solid fa-network-wired"></i>
            Remote Block Storage
          </h4>
        </div>
        <div class="col-5 text-end">
          <div class="btn-group">
            <button @click="createNewBlockStorage = true" class="btn btn-light">New Block Device</button>
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
      <div class="spinner-border" role="status" v-if="loadingBlockStorage">
        <span class="visually-hidden">Loading remote block storage devices. Please wait...</span>
      </div>
      <div v-if="blockDevices.length === 0">
        No remote block storage devices available
      </div>
      <div class="table-responsive" v-else>
        <table class="table table-borderless">
          <thead>
          <tr>
            <th scope="col">Name</th>
            <th scope="col">Storage Pool</th>
            <th scope="col">Status</th>
            <th scope="col">Size</th>
            <th scope="col">&nbsp;</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="blockDevice in blockDevices">
            <th scope="row">
              <i class="fa-solid fa-network-wired"></i>
              {{ blockDevice.name }}
            </th>
            <td>
              <i class="fa-regular fa-hard-drive"></i>
              {{ blockDevice.pool }}
            </td>
            <td class="text-success"><i class="fa-regular fa-circle-check"></i> Active</td>
            <td><span class="badge text-bg-dark">{{ blockDevice.size }}G</span></td>
            <td class="text-end">
              <span
                data-bs-toggle="modal"
                :data-bs-target="'#' + blockDevice.name"
                title="Show ISCSI config"
                class="text-secondary"
              >
                <i class="fa-regular fa-eye"></i>
              </span>

              <span
                  v-if="snapshotDevice === blockDevice.name && isCreatingSnapshot"
                  class="spinner-border text-secondary spinner-border-sm ms-2"
                  aria-hidden="true"
              >
              </span>
              <span
                  v-else
                  @click="takeSnapshot(blockDevice.pool, blockDevice.name)"
                  class="fa-regular fa-copy ms-2 text-secondary"
                  title="Take a snapshot"
              >
              </span>

              <span
                  v-if="deviceToBeDeleted === blockDevice.name && isDeletingBlockStorage"
                  class="spinner-border text-danger spinner-border-sm"
                  aria-hidden="true"
              >
              </span>
              <span
                  v-else
                  @click="deleteBlockStorage(blockDevice.pool, blockDevice.name)"
                  class="fa-regular fa-trash-can ms-2 text-danger"
                  title="Delete block storage"
              >
              </span>

              <div class="modal fade" :id="blockDevice.name" tabindex="-1" :aria-labelledby="blockDevice.name" aria-hidden="true">
                <div class="modal-dialog">
                  <div class="modal-content">
                    <div class="modal-header">
                      <h1 class="modal-title fs-5" id="exampleModalLabel">Remote Block Storage Config</h1>
                      <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                      <pre>{{ blockDevice.config }}</pre>
                    </div>
                    <div class="modal-footer">
                      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                  </div>
                </div>
              </div>

            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="col-md-4">
      <CreateBlockStorage @reload-block-storage="getBlockStorage()" v-if="createNewBlockStorage" />
    </div>
  </div>
</template>
