package app.grabbox.work

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import java.util.UUID
import java.util.concurrent.atomic.AtomicInteger

/** In-memory job table the service writes and the UI reads. */
object JobStore {

    data class Job(
        val id: String,
        val url: String,
        val title: String = "",
        val kind: String = "file",
        val quality: String = "best",
        val playlist: Boolean = false,
        val status: String = "queued",   // queued|running|done|error|canceled
        val percent: Float = 0f,         // 0..100, -1 = unknown
        val etaSec: Long = 0L,
        val attempt: Int = 1,
        val attempts: Int = 1,
        val filename: String? = null,
        val filePath: String? = null,
        val outDir: String,
        val error: String? = null,
        val hint: String? = null,
        val customName: String? = null,
        val createdAt: Long = System.currentTimeMillis(),
    ) {
        val active: Boolean get() = status == "queued" || status == "running"
    }

    private val counter = AtomicInteger(1)
    private val _jobs = MutableStateFlow<List<Job>>(emptyList())
    val jobs: StateFlow<List<Job>> = _jobs.asStateFlow()

    fun newJob(
        url: String, kind: String, quality: String, playlist: Boolean,
        outDir: String, customName: String?,
    ): Job {
        val job = Job(
            id = "j${counter.getAndIncrement()}-${UUID.randomUUID().toString().take(6)}",
            url = url, kind = kind, quality = quality, playlist = playlist,
            outDir = outDir, customName = customName,
            attempts = Engine.ladder(url).size,
        )
        _jobs.update { listOf(job) + it }
        return job
    }

    fun update(id: String, transform: (Job) -> Job) {
        _jobs.update { list -> list.map { if (it.id == id) transform(it) else it } }
    }

    fun get(id: String): Job? = _jobs.value.firstOrNull { it.id == id }

    fun hasActive(): Boolean = _jobs.value.any { it.active }

    fun clearFinished() {
        _jobs.update { list -> list.filter { it.active } }
    }
}
