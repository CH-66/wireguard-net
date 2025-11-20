<template>
  <div class="page-container">
    <div class="page-header mb-3">
      <h2>服务端管理</h2>
      <p class="text-secondary">管理 WireGuard 服务端配置和状态</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="serverStore.loading && !serverStore.serverInfo" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 未初始化状态 -->
    <div v-else-if="!serverStore.isInitialized" class="init-container">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon :size="24" color="#409EFF"><Warning /></el-icon>
            <span class="ml-2">服务端未初始化</span>
          </div>
        </template>
        
        <el-alert
          type="info"
          :closable="false"
          class="mb-3"
        >
          <p>欢迎使用 WireGuard 组网工具！在开始使用之前，请先初始化服务端配置。</p>
          <p class="mt-2">初始化将完成以下操作：</p>
          <ul class="mt-2" style="margin-left: 20px;">
            <li>生成服务端密钥对</li>
            <li>配置虚拟网络</li>
            <li>启用IP转发和NAT</li>
            <li>启动 WireGuard 服务</li>
          </ul>
        </el-alert>

        <el-form
          ref="initFormRef"
          :model="initForm"
          :rules="initRules"
          label-width="120px"
        >
          <el-form-item label="公网端点" prop="public_endpoint" required>
            <el-input
              v-model="initForm.public_endpoint"
              placeholder="例如: 192.168.1.100:51820"
            >
              <template #prepend>
                <el-icon><Link /></el-icon>
              </template>
            </el-input>
            <div class="form-tip">服务端的公网IP地址和端口，客户端将通过此地址连接</div>
          </el-form-item>

          <el-form-item label="监听端口" prop="listen_port">
            <el-input-number
              v-model="initForm.listen_port"
              :min="1"
              :max="65535"
              :step="1"
              controls-position="right"
            />
            <div class="form-tip">WireGuard 监听端口，默认 51820</div>
          </el-form-item>

          <el-form-item label="网络段" prop="network_cidr">
            <el-input
              v-model="initForm.network_cidr"
              placeholder="10.0.0.0/24"
            >
              <template #prepend>
                <el-icon><Connection /></el-icon>
              </template>
            </el-input>
            <div class="form-tip">虚拟网络的IP段，默认 10.0.0.0/24</div>
          </el-form-item>

          <el-form-item label="服务端IP" prop="server_ip">
            <el-input
              v-model="initForm.server_ip"
              placeholder="10.0.0.1"
            >
              <template #prepend>
                <el-icon><Location /></el-icon>
              </template>
            </el-input>
            <div class="form-tip">服务端在虚拟网络中的IP地址，默认 10.0.0.1</div>
          </el-form-item>

          <el-form-item label="强制重新初始化" prop="force">
            <el-switch v-model="initForm.force" />
            <div class="form-tip text-warning">警告：强制重新初始化将清除所有现有配置</div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              :loading="serverStore.loading"
              @click="handleInitialize"
            >
              <el-icon class="mr-1"><Check /></el-icon>
              初始化服务端
            </el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 已初始化状态 -->
    <div v-else class="server-info-container">
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card shadow="hover" class="mb-3">
            <template #header>
              <div class="card-header">
                <div>
                  <el-icon :size="20" color="#67C23A"><SuccessFilled /></el-icon>
                  <span class="ml-2">服务端信息</span>
                </div>
                <div>
                  <el-button
                    type="primary"
                    size="small"
                    :loading="serverStore.loading"
                    @click="handleReload"
                  >
                    <el-icon class="mr-1"><Refresh /></el-icon>
                    重载配置
                  </el-button>
                  <el-button
                    type="warning"
                    size="small"
                    :loading="serverStore.loading"
                    @click="showReinitDialog = true"
                  >
                    <el-icon class="mr-1"><Setting /></el-icon>
                    重新初始化
                  </el-button>
                </div>
              </div>
            </template>

            <el-descriptions :column="2" border>
              <el-descriptions-item label="服务端ID">
                <el-tag type="info">{{ serverStore.serverInfo?.id }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">
                {{ formatDateTime(serverStore.serverInfo?.created_at || null) }}
              </el-descriptions-item>
              <el-descriptions-item label="虚拟IP">
                <el-tag type="success">{{ serverStore.serverInfo?.virtual_ip }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="监听端口">
                <el-tag>{{ serverStore.serverInfo?.listen_port }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="网络段">
                {{ serverStore.serverInfo?.network_cidr }}
              </el-descriptions-item>
              <el-descriptions-item label="公网端点">
                <el-tag type="warning">{{ serverStore.serverInfo?.public_endpoint || '-' }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="公钥" :span="2">
                <el-input
                  :model-value="serverStore.serverInfo?.public_key"
                  readonly
                  size="small"
                >
                  <template #append>
                    <el-button
                      @click="copyToClipboard(serverStore.serverInfo?.public_key || '')"
                    >
                      <el-icon><DocumentCopy /></el-icon>
                    </el-button>
                  </template>
                </el-input>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 重新初始化确认对话框 -->
    <el-dialog
      v-model="showReinitDialog"
      title="确认重新初始化"
      width="500px"
    >
      <el-alert
        type="warning"
        :closable="false"
        class="mb-3"
      >
        <p><strong>警告：此操作将删除所有现有配置！</strong></p>
        <p class="mt-2">重新初始化将：</p>
        <ul style="margin-left: 20px;">
          <li>删除所有节点配置</li>
          <li>重新生成服务端密钥</li>
          <li>重置网络配置</li>
        </ul>
        <p class="mt-2">此操作<strong>不可恢复</strong>，请谨慎操作！</p>
      </el-alert>

      <el-form :model="reinitForm" label-width="120px">
        <el-form-item label="公网端点" required>
          <el-input
            v-model="reinitForm.public_endpoint"
            placeholder="例如: 192.168.1.100:51820"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showReinitDialog = false">取消</el-button>
        <el-button
          type="danger"
          :loading="serverStore.loading"
          @click="handleReinitialize"
        >
          确认重新初始化
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Warning,
  Check,
  Link,
  Connection,
  Location,
  SuccessFilled,
  Refresh,
  Setting,
  DocumentCopy
} from '@element-plus/icons-vue'
import { useServerStore } from '@/stores/server'
import { formatDateTime } from '@/utils/format'
import { validatePort, validateCIDR, validateIPv4, validateEndpoint } from '@/utils/validator'

const serverStore = useServerStore()

// 表单引用
const initFormRef = ref<FormInstance>()

// 初始化表单数据
const initForm = reactive({
  public_endpoint: '',
  listen_port: 51820,
  network_cidr: '10.0.0.0/24',
  server_ip: '10.0.0.1',
  force: false
})

// 表单验证规则
const initRules: FormRules = {
  public_endpoint: [
    { required: true, message: '请输入公网端点', trigger: 'blur' },
    { validator: validateEndpoint, trigger: 'blur' }
  ],
  listen_port: [
    { validator: validatePort, trigger: 'blur' }
  ],
  network_cidr: [
    { validator: validateCIDR, trigger: 'blur' }
  ],
  server_ip: [
    { validator: validateIPv4, trigger: 'blur' }
  ]
}

// 重新初始化对话框
const showReinitDialog = ref(false)
const reinitForm = reactive({
  public_endpoint: ''
})

// 初始化服务端
async function handleInitialize() {
  if (!initFormRef.value) return
  
  await initFormRef.value.validate(async (valid) => {
    if (valid) {
      // 如果是强制初始化，需要二次确认
      if (initForm.force) {
        try {
          await ElMessageBox.confirm(
            '强制初始化将删除所有现有配置，此操作不可恢复，是否继续？',
            '警告',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning'
            }
          )
        } catch {
          return
        }
      }

      const success = await serverStore.initializeServer(initForm)
      if (success) {
        resetForm()
      }
    }
  })
}

// 重新初始化
async function handleReinitialize() {
  if (!reinitForm.public_endpoint) {
    ElMessage.warning('请输入公网端点')
    return
  }

  const success = await serverStore.initializeServer({
    public_endpoint: reinitForm.public_endpoint,
    force: true
  })

  if (success) {
    showReinitDialog.value = false
    reinitForm.public_endpoint = ''
  }
}

// 重载配置
async function handleReload() {
  try {
    await ElMessageBox.confirm(
      '确定要重载 WireGuard 配置吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    await serverStore.reloadWireguard()
  } catch {
    // 用户取消
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

// 重置表单
function resetForm() {
  if (initFormRef.value) {
    initFormRef.value.resetFields()
  }
}

// 页面加载时获取服务端信息
onMounted(() => {
  serverStore.fetchServerInfo()
})
</script>

<style scoped>
.page-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 24px;
}

.page-header .text-secondary {
  margin-top: 8px;
  font-size: 14px;
}

.loading-container {
  background: var(--bg-white);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.form-tip {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.text-warning {
  color: var(--warning-color);
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}
</style>
