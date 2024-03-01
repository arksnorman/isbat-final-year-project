<script setup>
import {onMounted, ref} from 'vue'
import axios from "../axios.js"
import CreateStoragePool from "./CreateStoragePool.vue";
import ExtendPool from "./ExtendPool.vue";

defineProps({
  msg: String,
})

const pools = ref([])
const loadingPools = ref(false)
const errorMessage = ref("")
const selectedPools = ref([])
const isCreateStoragePool = ref(false)
const successMessage = ref("")
const isDeletingPool = ref(false)
const poolsToBeDeleted = ref([])
const isExtendPool = ref(false)
const poolToBeExtended = ref("")

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

function clearMessages() {
  setTimeout(() => {
    successMessage.value = ""
    errorMessage.value = ""
  }, 5000)
}

async function deletePools(volumeGroups) {
  if (!confirm("Are you sure you want to proceed with action?")) {
    return
  }
  poolsToBeDeleted.value = volumeGroups
  isDeletingPool.value = true
  try {
    const res = await axios.delete("/storage-pools", {data: {volumeGroups: volumeGroups}})
    if (res.status === 204) {
      successMessage.value = "Storage pool(s) deleted successfully"
      selectedPools.value = []
      await getStoragePools()
    } else {
      errorMessage.value = "Error: " + res.statusText
    }
  } catch (e) {
    errorMessage.value = e.toString()
  }
  isDeletingPool.value = false
  clearMessages()
}

async function extendPool(poolName) {
  if (!confirm("Are you sure you want to proceed with action?")) {
    return
  }
  poolsToBeDeleted.value = volumeGroups
  isDeletingPool.value = true
  try {
    const res = await axios.delete("/storage-pools", {data: {volumeGroups: volumeGroups}})
    if (res.status === 204) {
      successMessage.value = "Storage pool(s) deleted successfully"
      selectedPools.value = []
      await getStoragePools()
    } else {
      errorMessage.value = "Error: " + res.statusText
    }
  } catch (e) {
    errorMessage.value = e.toString()
  }
  isDeletingPool.value = false
  clearMessages()
}

onMounted(async () => {
  await getStoragePools()
})

function triggerPoolExtension(name) {
  poolToBeExtended.value = name
  isExtendPool.value = true
}

</script>



<template>
  <div class="row">
    <div class="col-8">
      <div class="row">
        <div class="col-7">
          <h4>
            <i class="fa-regular fa-hard-drive"></i>
            Storage Pools
          </h4>
        </div>
        <div class="col-5 text-end">
          <div class="btn-group">
            <button @click="isCreateStoragePool = true" class="btn btn-light">New Storage Pool</button>
            <button
              v-if="selectedPools.length > 0"
              @click="deletePools(selectedPools)"
              class="btn btn-danger"
            >
              Delete
            </button>
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
      <div class="spinner-border" role="status" v-if="loadingPools">
        <span class="visually-hidden">Loading storage pools. Please wait...</span>
      </div>
      <div v-if="pools.length === 0">
        No storage pools available
      </div>
      <div class="table-responsive" v-else>
        <table class="table table-borderless">
        <thead>
          <tr>
            <th scope="col">Pool name</th>
            <th scope="col">Status</th>
            <th scope="col">Usage</th>
            <th scope="col">&nbsp;</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pool in pools">
            <th scope="row">
              <div class="form-check-inline">
                <input
                  class="form-check-input"
                  type="checkbox"
                  :value="pool.name"
                  id="flexCheckDefault"
                  v-model="selectedPools"
                >
              </div>
              <i class="fa-regular fa-hard-drive"></i>
              {{ pool.name }}
            </th>
            <td class="text-success"><i class="fa-regular fa-circle-check"></i> Active</td>
            <td><span class="badge text-bg-dark">{{ pool.usedSize }}G/{{ pool.size }}G</span></td>
            <td class="text-end">
              <span @click="triggerPoolExtension(pool.name)">
                <i title="Expand pool storage" class="fa-regular fa-square-plus"></i> Extend |
              </span>
              <span
                v-if="poolsToBeDeleted.includes(pool.name) && isDeletingPool"
                class="spinner-border text-danger spinner-border-sm"
                aria-hidden="true"
              >
              </span>
              <span
                v-else
                @click="deletePools([pool.name])"
                class="fa-regular fa-trash-can ms-2 text-danger"
                title="Delete Storage Pool"
              >
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
    <div class="col-md-4">
      <CreateStoragePool @reload-pools="getStoragePools()" v-if="isCreateStoragePool" />
      <ExtendPool @reload-pools="getStoragePools()" :pool-name="poolToBeExtended" v-if="isExtendPool" />
    </div>
  </div>
</template>
