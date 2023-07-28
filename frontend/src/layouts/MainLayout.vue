<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          Siteparser
        </q-toolbar-title>

        <div>v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
    >
      <q-list>
        <q-item-label header>Menu</q-item-label>

        <q-item to="/jobs">
          <q-item-section avatar><q-icon name="edit_calendar"/></q-item-section>
          <q-item-section>
            <q-item-label>Jobs</q-item-label>
            <q-item-label caption>Manage scheduled jobs</q-item-label>
          </q-item-section>
        </q-item>

        <q-item to="/items">
          <q-item-section avatar><q-icon name="article"/></q-item-section>
          <q-item-section>
            <q-item-label>Items</q-item-label>
            <q-item-label caption>View scraped items</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'MainLayout',

  components: {
  },

  setup () {
    const leftDrawerOpen = ref(false)

    return {
      leftDrawerOpen,
      toggleLeftDrawer () {
        leftDrawerOpen.value = !leftDrawerOpen.value
      }
    }
  }
})
</script>
