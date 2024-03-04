<script setup>
import StoragePools from "./components/StoragePool/StoragePools.vue";
import {computed, ref} from "vue";
import NotFound from "./components/NotFound.vue";
import BlockStorage from "./components/BlockStorage/BlockStorage.vue";
import Snapshots from "./components/Snapshots/Snapshots.vue";


const routes = {
  "/": StoragePools,
  "/block-storage": BlockStorage,
  "/snapshots": Snapshots
}

const currentPath = ref(window.location.hash)

window.addEventListener('hashchange', () => {
  currentPath.value = window.location.hash
})

const currentView = computed(() => {
  return routes[currentPath.value.slice(1) || '/'] || NotFound
})

</script>

<template>
  <nav class="navbar navbar-expand-lg bg-body-tertiary">
    <div class="container">
      <a class="navbar-brand" href="#">
        <img src="./assets/hdd.svg" alt="Bootstrap" width="40" height="40">
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNavAltMarkup">
        <div class="navbar-nav">
          <a
            class="nav-link"
            :class="{ active: (currentPath === '#/')}"
            href="#/"
          >
            Storage Pools
          </a>
          <a
            class="nav-link"
            :class="{ active: (currentPath === '#/block-storage')}"
            href="#/block-storage"
          >
            Block Storage
          </a>
          <a
            class="nav-link"
            :class="{ active: (currentPath === '#/snapshots')}"
            href="#/snapshots"
          >
            Snapshots
          </a>
<!--          <a class="nav-link" href="#">{{ currentPath }}</a>-->
        </div>
      </div>
    </div>
  </nav>
  <div class="container mt-5">
    <component :is="currentView" />
  </div>
</template>
