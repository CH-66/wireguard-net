/**
 * 下载工具函数
 */

/**
 * 从Content-Disposition响应头提取文件名
 * @param disposition Content-Disposition头内容
 * @returns 文件名
 */
export function extractFilename(disposition: string | null): string {
  if (!disposition) return 'download'
  
  // 尝试匹配 filename="xxx" 或 filename*=UTF-8''xxx
  const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
  const matches = filenameRegex.exec(disposition)
  
  if (matches && matches[1]) {
    let filename = matches[1].replace(/['"]/g, '')
    // 处理 UTF-8 编码的文件名
    if (filename.startsWith('UTF-8\'\'')) {
      filename = decodeURIComponent(filename.substring(7))
    }
    return filename
  }
  
  return 'download'
}

/**
 * 下载Blob数据为文件
 * @param blob Blob对象
 * @param filename 文件名
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.style.display = 'none'
  
  document.body.appendChild(link)
  link.click()
  
  // 清理
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

/**
 * 处理文件下载响应
 * @param response Axios响应对象
 * @param defaultFilename 默认文件名
 */
export function handleDownloadResponse(response: any, defaultFilename: string = 'download'): void {
  const disposition = response.headers['content-disposition']
  const filename = extractFilename(disposition) || defaultFilename
  downloadBlob(response.data, filename)
}
