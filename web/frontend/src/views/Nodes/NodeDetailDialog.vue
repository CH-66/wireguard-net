<template>
  <el-dialog
    v-model="dialogVisible"
    title="节点详情"
    width="700px"
    @close="handleClose"
  >
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="nodeDetail">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="节点ID">
          <el-tag type="info">{{ nodeDetail.id }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="节点名称">
          <strong>{{ nodeDetail.node_name }}</strong>
        </el-descriptions-item>
        <el-descriptions-item label="平台类型">
          <el-tag :type="nodeDetail.platform === 'linux' ? 'success' : 'primary'">
            <el-icon class="mr-1"><Monitor /></el-icon>
            {{ nodeDetail.platform.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="虚拟IP">
          <el-tag type="success">{{ nodeDetail.virtual_ip }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">
          {{ formatDateTime(nodeDetail.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间" :span="2">
          {{ formatDateTime(nodeDetail.updated_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">
          {{ nodeDetail.description || '-' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <div class="key-section">
        <h4>密钥信息</h4>
        <el-alert
          type="warning"
          :closable="false"
          class="mb-3"
        >
          <p><strong>安全提示：</strong>私钥是敏感信息，请妥善保管，不要泄露给他人！</p>
        </el-alert>

        <el-form label-width="80px">
          <el-form-item label="公钥">
            <el-input
              :model-value="nodeDetail.public_key"
              readonly
              size="small"
            >
              <template #append>
                <el-button @click="copyToClipboard(nodeDetail.public_key)">
                  <el-icon><DocumentCopy /></el-icon>
                  复制
                </el-button>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="私钥">
            <el-input
              :model-value="nodeDetail.private_key || ''"
              readonly
              type="textarea"
              :rows="3"
              size="small"
            >
              <template #append>
                <el-button @click="copyToClipboard(nodeDetail.private_key || '')">
                  <el-icon><DocumentCopy /></el-icon>
                  复制
                </el-button>
              </template>
            </el-input>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button
        type="primary"
        @click="handleDownloadConfig"
      >
        <el-icon class="mr-1"><Download /></el-icon>
        下载配置
      </el-button>
      <el-button
        type="success"
        @click="handleDownloadScript"
      >
        <el-icon class="mr-1"><Download /></el-icon>
        下载脚本
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Monitor, DocumentCopy, Download } from '@element-plus/icons-vue'
import { useNodesStore } from '@/stores/nodes'
import { downloadNodeConfig, downloadNodeScript } from '@/api/downloads'
import { formatDateTime } from '@/utils/format'
import type { NodeDetail } from '@/types/node'

const props = defineProps<{
  visible: boolean
  nodeId: number | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const nodesStore = useNodesStore()

const dialogVisible = ref(false)
const loading = ref(false)
const nodeDetail = ref<NodeDetail | null>(null)

// 监听visible变化
watch(() => props.visible, async (val) => {
  dialogVisible.value = val
  if (val && props.nodeId) {
    await loadNodeDetail()
  }
})

watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

// 加载节点详情
async function loadNodeDetail() {
  if (!props.nodeId) return
  
  loading.value = true
  try {
    nodeDetail.value = await nodesStore.fetchNodeDetail(props.nodeId)
  } finally {
    loading.value = false
  }
}

// 复制到剪贴板
async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

// 下载配置文件
async function handleDownloadConfig() {
  if (!props.nodeId) return
  try {
    await downloadNodeConfig(props.nodeId)
  } catch (error) {
    // 错误已在API层处理
  }
}

// 下载安装脚本
async function handleDownloadScript() {
  if (!props.nodeId) return
  try {
    await downloadNodeScript(props.nodeId)
  } catch (error) {
    // 错误已在API层处理
  }
}

// 关闭对话框
function handleClose() {
  dialogVisible.value = false
  nodeDetail.value = null
}
</script>

<style scoped>
.loading-container {
  padding: 20px;
}

.key-section {
  margin-top: 20px;
}

.key-section h4 {
  margin: 0 0 16px 0;
  color: var(--text-primary);
  font-size: 16px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}

:deep(.el-textarea__inner) {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}
</style>
