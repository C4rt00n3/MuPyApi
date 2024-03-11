package com.mupy.soundpy.utils

import android.app.NotificationManager
import android.content.Context
import android.net.Uri
import android.os.Build
import android.support.v4.media.session.MediaSessionCompat
import androidx.annotation.RequiresApi
import com.google.android.exoplayer2.ExoPlayer
import com.google.android.exoplayer2.MediaItem
import com.google.android.exoplayer2.MediaMetadata
import com.google.android.exoplayer2.Player
import com.google.android.exoplayer2.ui.PlayerNotificationManager
import com.mupy.soundpy.ContextMain
import com.mupy.soundpy.R
import com.mupy.soundpy.database.Music
import com.mupy.soundpy.database.PlaylistWithMusic
import java.io.File


class SoundPy(
    private val context: Context,
    var playlist: PlaylistWithMusic,
    private val viewModel: ContextMain,
    private var playerNotificationManager: PlayerNotificationManager = PlayerNotificationManager.Builder(
        context, 151, "soundPy_notification"
    ).setChannelImportance(NotificationManager.IMPORTANCE_MAX)
        .setChannelNameResourceId(R.string.app_name).build(),
) {
    var order = "DESC"

    // private val utils = Utils()
    private var cache = mutableListOf<MediaItem>()
    val player = ExoPlayer.Builder(context).setHandleAudioBecomingNoisy(true).build()
    private val listener = object : Player.Listener {
        @RequiresApi(Build.VERSION_CODES.P)
        override fun onMediaItemTransition(mediaItem: MediaItem?, reason: Int) {
            super.onMediaItemTransition(mediaItem, reason)
            if (reason != Player.MEDIA_ITEM_TRANSITION_REASON_SEEK) {
                player.pause()
                if (!player.isPlaying) player.play()
                viewModel.setMusic(getMetadata(mediaItem?.mediaMetadata))
                viewModel.run {
                    setProgress(0f)
                    setCurrentPosition(0)
                }
            }
        }

        @RequiresApi(Build.VERSION_CODES.P)
        override fun onIsPlayingChanged(isPlaying: Boolean) {
            viewModel.setPause(isPlaying)
            if (isPlaying) {
                getMetadata().let {
                    viewModel.setMusic(it)
                }
                viewModel.startTime()
            }
        }
    }

    init {
        init(playlist)
    }

    fun duration(): Long {
        return player.duration
    }

    fun orderBy() {
        if (order == "DESC") {
            cache = cache.reversed().toMutableList()
            playlist = playlist.copy(music = playlist.music.reversed().toMutableList())
        } else if (order != "ASC") {
            cache = cache.shuffled().toMutableList()
            playlist = playlist.copy(music = playlist.music.shuffled().toMutableList())
        }
    }

    fun reload(playlistWithMusic: PlaylistWithMusic) {
        player.removeMediaItems(0, player.mediaItemCount)
        playlist = playlistWithMusic
        loadListMediaItems(playlistWithMusic)
    }

    private fun init(playlistP: PlaylistWithMusic) {
        loadListMediaItems(playlistP)
        orderBy()
        player.apply {
            addMediaItems(cache)
            prepare()
            addListener(listener)
            repeatMode = ExoPlayer.REPEAT_MODE_ALL
        }
        if (cache.isNotEmpty()) showNotification()
        if (playlist.music.isNotEmpty()) getMetadata().let { viewModel.setMusic(it) }
    }

    private fun showNotification() {
        playerNotificationManager.setPlayer(null)
        val mediaSession = MediaSessionCompat(context, "Music")
        mediaSession.isActive = true
        playerNotificationManager.apply {
            setColorized(true)
            setMediaSessionToken(mediaSession.sessionToken)
            setUseChronometer(true)
            setSmallIcon(R.mipmap.ic_launcher)
            setUseRewindActionInCompactView(true)
            setUseRewindAction(true)
            setUsePlayPauseActions(true)
            setUsePreviousActionInCompactView(true)
            setUseNextActionInCompactView(true)
            setUsePreviousActionInCompactView(true)
            setUseFastForwardAction(true)
            setUseRewindAction(true)
            setPlayer(player)
        }
    }

    // Carrega a lista de passado por parametro
    private fun loadListMediaItems(playlist: PlaylistWithMusic) {
        val music = playlist.music
        music.apply {
            mapIndexed { int, music ->
                cache.add(
                    addMediaItem(
                        Uri.parse(
                            music.directory
                        ), music
                    )
                )
            }
        }
    }

    // Cria um MediaItem a parti de um Music.
    private fun addMediaItem(uri: Uri, music: Music): MediaItem {
        return MediaItem.Builder().setUri(uri).apply { setMediaMetadata(setMetaData(music)) }
            .build()
    }

    // Adiciona os metados há mediaItem.
    private fun setMetaData(music: Music): MediaMetadata = MediaMetadata.Builder().apply {
        setAlbumArtist(music.author)
        setAlbumTitle(music.title)
        setTitle(music.title)
        setArtist(music.title)
        setSubtitle(music.name)
        music.bitImage?.let {
            setArtworkData(it)
        }
        setArtworkUri(Uri.parse(music.thumb))
        setDescription(music.title)
    }.build()

    fun addMusic(music: Music) {
        val directory = File(music.directory)

        if (!directory.exists() && music.directory.isBlank()) return

        val md = addMediaItem(Uri.parse(music.directory), music)

        if (order == "ASC") {
            cache.add(md)
            player.addMediaItem(md)
        } else if (order == "DESC") {
            cache.add(0, md)
            player.addMediaItem(0, md)
        } else {
            val disorder = (0 until cache.size).random()
            cache.add(disorder, md)
            player.addMediaItem(disorder, md)
        }
        player.prepare()
    }

    fun releasePlayerAndNotification() {
        player.removeMediaItems(0, player.mediaItemCount)
        player.removeListener(listener)
        playerNotificationManager.setPlayer(null)
        player.release()
        cache.clear()
    }

    fun removedMusic(music: Music) {
        val position = playlist.music.indexOf(music)
        if (position != -1) {
            playlist =
                playlist.copy(music = playlist.music.filter { it.id != music.id }.toMutableList())
            cache.removeAt(position)
            player.setMediaItems(cache)
            player.prepare()
        }
    }

    fun getMetadata(metaData: MediaMetadata? = player.mediaMetadata): Music {
        return Music(
            author = metaData?.artist.toString(),
            thumb = metaData?.artworkUri.toString(),
            title = metaData?.albumTitle.toString(),
            url = metaData?.description.toString(),
            name = metaData?.subtitle.toString(),
            bitImage = metaData?.artworkData,
            directory = "",
            playlistId = 0
        )
    }

    fun stream(uri: Uri, music: Music) {
        val md = addMediaItem(uri, music)
        cache.add(md)
        player.addMediaItem(md)
        player.prepare()
        open(music)
        player.play()
        player.repeatMode = ExoPlayer.REPEAT_MODE_ALL
    }

    fun open(music: Music) {
        for (i in 0 until cache.size) {
            cache[i].mediaMetadata.apply {
                if (title.toString() == music.title) {
                    player.seekTo(i, 0)
                    return
                }
            }
        }
    }

    fun setVolume(one: Float) {
        player.volume = one
    }

    fun reapt(boolean: Boolean) {
        if (!boolean) {
            // Se estiver em loop, desativa o loop
            player.repeatMode = Player.REPEAT_MODE_OFF
        } else {
            // Se não estiver em loop, ativa o loop
            player.repeatMode = Player.REPEAT_MODE_ONE
        }
    }

    fun timeUse(time: Int): String {
        val seconds = time / 1000f
        val minutes = seconds / 60
        val remainingSeconds = seconds % 60
        return String.format("%02d:%02d", minutes.toInt(), remainingSeconds.toInt())
    }
}