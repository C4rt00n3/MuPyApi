package com.mupy.soundpy

import android.content.Context
import android.net.Uri
import android.os.Build
import android.util.Log
import android.widget.Toast
import androidx.annotation.RequiresApi
import androidx.compose.runtime.Composable
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import androidx.palette.graphics.Palette
import com.mupy.soundpy.database.AppDatabase
import com.mupy.soundpy.database.Music
import com.mupy.soundpy.database.MyPlaylists
import com.mupy.soundpy.database.PlaylistWithMusic
import com.mupy.soundpy.models.Menu
import com.mupy.soundpy.models.PlayListData
import com.mupy.soundpy.network.ApiViewModel
import com.mupy.soundpy.utils.SoundPy
import com.mupy.soundpy.utils.Utils
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

class ContextMain(
    private val context: Context, private val dataBase: AppDatabase?
) : ApiViewModel() {
    private val utils = Utils()
    private var playlistImage: ByteArray? = null

    private val _currentPlaylist = MutableLiveData<PlaylistWithMusic?>(null)
    private val currentPlaylist: LiveData<PlaylistWithMusic?> = _currentPlaylist

    private val _currentPosition = MutableLiveData(0)
    val currentPosition: LiveData<Int> = _currentPosition

    private val _soundPy: MutableLiveData<SoundPy> = MutableLiveData(
        SoundPy(
            context, currentPlaylist.value ?: PlaylistWithMusic(
                playlist = MyPlaylists(0, null, context.getString(R.string.sem_nada)),
                mutableListOf()
            ), this
        )
    )
    val soundPy: LiveData<SoundPy> = _soundPy

    private val _palette = MutableLiveData<Palette?>(null)
    val palette: LiveData<Palette?> = _palette

    private val _pause = MutableLiveData(_soundPy.value?.player?.isPlaying == true)
    val pause: LiveData<Boolean> = _pause

    private val _mute = MutableLiveData(false)
    val mute: LiveData<Boolean> = _mute

    private val _menu = MutableLiveData(Menu(false) @Composable {})
    val menu: LiveData<Menu> = _menu

    private val _repeat = MutableLiveData(false)
    val repeat: LiveData<Boolean> = _repeat

    private val _progress = MutableLiveData(0f)
    val progress: LiveData<Float> = _progress

    // private val _stream = MutableLiveData(StreamYt(""))
    // val stream: LiveData<StreamYt> = _stream

    private val _showModal = MutableLiveData(false)
    val showModal: LiveData<Boolean> = _showModal

    private val _music = MutableLiveData<Music?>(null)
    val music: LiveData<Music?> = _music

    private val _saved = MutableLiveData(utils.getMusicsSaved(context))
    val saved: LiveData<Array<Music>> = _saved

    private val _myPlaylist = MutableLiveData(
        arrayOf<PlaylistWithMusic>()
    )
    val myPlaylist: LiveData<Array<PlaylistWithMusic>> = _myPlaylist

    private val _playListsCards = MutableLiveData(
        arrayListOf<PlayListData>()
    )
    val playListsCards: LiveData<ArrayList<PlayListData>> = _playListsCards

    private fun setSaved() {
        _saved.value = utils.getMusicsSaved(context)
    }

    fun getPlaylists() {
        viewModelScope.launch {
            try {
                val result = repository.getPlaylists("generos mais ouvidos no brasil")
                if (result.isNotEmpty()) _playListsCards.value = result
            } catch (error: Exception) {
                Log.e("Error", error.message.toString())
            } finally {
                this.cancel()
                if (_playListsCards.value?.isEmpty() == true) {
                    _playListsCards.value = arrayListOf(
                        PlayListData(
                            "https://lh3.googleusercontent.com/18eW5KsqS0J0Q9pX3y6KqrfrsJB5-U_LMbEJ_s2SwGSeCm2Th_XMebciVMg8Upg372kTotCy8QSh6T4h=w544-h544-l90-rj",
                            "RDCLAK5uy_k5faEHND0iXJljeASESqJ3A8UtRr2FL00",
                            "Topnejo",
                            ""
                        ), PlayListData(
                            "https://yt3.googleusercontent.com/mhawOLp1YtaUXhAyQnvGIqNWP9oQ9Ry7QaVXEd_ymnTAC4eZ0pVHOIX0HD5ZZuW6mj1r--rFqWNQ=s576",
                            "PLNyUJbuBiyw0SmnPYy4QfkDnpgq85fJBl",
                            "TRAP BRASIL 2023",
                            ""
                        ), PlayListData(
                            "https://lh3.googleusercontent.com/Nbv9b6PTaELOo14LJO90khFgsXf62QStHsJtpaV1P0yLJwcskFCaONFLdaXGQYH7e5-7iMfhsx4tIQ=w544-h544-l90-rj",
                            "RDCLAK5uy_nRxkdjoJYfKXKh4HyRtpuHKfmIfSH2khY",
                            "Funk de Natal",
                            ""
                        ), PlayListData(
                            "https://lh3.googleusercontent.com/w8QDcpITg-64iylxia0Z4oWzbmlkHdSeSNyGslc_0ZcJgCtgLHkhugunsDRh_t87UQadn_si6-gPpvI=w544-h544-l90-rj",
                            "RDCLAK5uy_nZiG9ehz_MQoWQxY5yElsLHCcG0tv9PRg",
                            "Os maiores sucessos do rock clássico",
                            ""
                        ), PlayListData(
                            "https://lh3.googleusercontent.com/ih5QdpqpkVNRXtD-joBWj3jo1woxAXJFyAoA3hWYNWAKX0M9B825HH2VOh7aDX-unf67oyCyJGN9TljR=w544-h544-l90-rj",
                            "RDCLAK5uy_nmS3YoxSwVVQk9lEQJ0UX4ZCjXsW_psU8",
                            "Pop's Biggest Hits",
                            ""
                        )
                    )
                }
            }
        }
    }

    fun setPlaylistImage(image: ByteArray?) {
        playlistImage = image
    }

    fun setMusic(m: Music?) {
        _music.value = m
        if (m?.bitImage != null) m.bitImage?.let { byte ->
            utils.toBitmap(byte)?.let {
                _palette.value = Palette.from(it).generate()
            }
        }
    }

    fun setMute(boolean: Boolean) {
        _mute.value = boolean
        _soundPy.value?.setVolume(if (!boolean) 1f else 0f)
    }

    fun setRepeat(boolean: Boolean) {
        _repeat.value = boolean
        _soundPy.value?.reapt(boolean)
    }

    fun setMenu(menu: Menu) {
        _menu.value = menu
    }

    fun setShowModal(boolean: Boolean) {
        _showModal.value = boolean
    }

    fun setCurrentPosition(int: Int) {
        _currentPosition.value = int
    }

    @RequiresApi(Build.VERSION_CODES.P)
    fun startTime() {
        viewModelScope.launch {
            val duration = _soundPy.value?.duration()?.toFloat() ?: 0f
            while (_pause.value == true) {
                setProgress(0f)
                val currentPosition = _soundPy.value?.player?.currentPosition?.toInt() ?: 0
                _currentPosition.value = currentPosition
                setProgress(
                    (currentPosition.toFloat() / 1000f) / ((duration) / 1000f)
                )
                delay(1000)
            }
            this.cancel()
        }
    }

    fun removeElementMyPlaylist(myPlaylists: PlaylistWithMusic) {
        viewModelScope.launch {
            _myPlaylist.value =
                _myPlaylist.value?.filter { it.playlist.name != myPlaylists.playlist.name }
                    ?.toTypedArray()
            dataBase?.service()?.delete(myPlaylists.playlist)
            this.cancel()
        }
    }

    fun addElementMyPlaylist(myPlaylists: MyPlaylists) {
        viewModelScope.launch {
            dataBase?.service()?.createMyPlaylist(myPlaylists.thumb, myPlaylists.name!!)
            getFiles()
            this.cancel()
        }
    }

    fun setProgress(float: Float) {
        _progress.value = float
    }

    fun setPause(boolean: Boolean) {
        _pause.value = boolean
    }

    private suspend fun saveInData(music: Music): Boolean =
        withContext((viewModelScope.coroutineContext)) {
            val existsInBank = dataBase?.service()?.getMusic(music.playlistId!!, music.url)
            if (existsInBank == false) {
                dataBase?.service()?.createMusic(music)
                _soundPy.value?.addMusic(music)
            }
            existsInBank == false
        }

    // Assuming the existence of the Music, PlaylistWithMusic, and other required types and objects
    @RequiresApi(Build.VERSION_CODES.P)
    fun download(
        music: Music, myPlaylists: PlaylistWithMusic, callBack: () -> Unit
    ) {
        viewModelScope.launch {
            try {
                val result = repository.download(music.url)
                utils.createFile(music.title, result.bytes(), context).let {
                    saveInData(it.copy(playlistId = myPlaylists.playlist.uid))
                    _soundPy.value?.addMusic(it)
                }
            } catch (error: Exception) {
                Log.e("Error", error.toString())
            } finally {
                callBack()
                getFiles()
                Toast.makeText(
                    context, context.getString(R.string.musica_baixada), Toast.LENGTH_SHORT
                ).show()
                this.cancel()
            }
        }
    }

    private suspend fun deleteMusicInDb(
        music: Music,
    ): Boolean {
        // check if it exists in the bank
        return withContext(Dispatchers.IO) {
            dataBase?.service()?.deleteMusic(music.url, music.playlistId)
            dataBase?.service()?.existMusic(music.url) == true
        }
    }

    private fun routineMusic() {
        viewModelScope.launch {
            val musics = dataBase?.service()?.gelAllMusics() ?: listOf()
            for (m in _saved.value ?: arrayOf()) {
                var contais = 0
                for (n in musics) {
                    if (n.url == m.url) contais++
                }
                if (contais == 0) {
                    utils.deleteMusic(m)
                }
            }
            setSaved()
            cancel()
        }
    }

    @RequiresApi(Build.VERSION_CODES.P)
    fun deleteMusic(
        music: Music, callBack: () -> Unit
    ) {
        viewModelScope.launch {
            try {
                // delete in directory
                val exist = deleteMusicInDb(music)
                if (!exist) {
                    withContext(Dispatchers.IO) {
                        val file = File(music.directory)
                        if (file.exists()) file.delete()
                    }
                }

            } catch (err: Exception) {
                Log.e("Error", "$err")
            } finally {
                _soundPy.value?.removedMusic(music)
                callBack()
                Toast.makeText(
                    context, context.getString(R.string.musica_removida), Toast.LENGTH_SHORT
                ).show()
                this.cancel()
            }
        }
    }

    private fun recoilPlaylists() {
        viewModelScope.launch {
            val playlists = withContext(Dispatchers.IO) {
                dataBase?.service()?.getAllPlaylistsWithMusic()?.toList() ?: emptyList()
            }
            _myPlaylist.value = playlists.toTypedArray()
            val currentPlaylist =
                playlists.firstOrNull { it.playlist.name == context.getString(R.string.minhas_musicas) }
            _currentPlaylist.value = currentPlaylist
        }
    }

    private fun getFiles() {
        viewModelScope.launch {
            try {
                recoilPlaylists()
                setSaved()
                val myp =
                    dataBase?.service()?.getAllPlaylistsWithMusic()?.toTypedArray() ?: arrayOf()
                _myPlaylist.value = myp
                _currentPlaylist.value =
                    myp.find { it.playlist.uid == _currentPlaylist.value?.playlist?.uid }
            } catch (err: Exception) {
                Log.e("Error", err.message.toString())
            } finally {
                this.cancel()
            }
        }
    }

    private fun setSoundPy(): Job = viewModelScope.launch {
        _soundPy.value = SoundPy(
            context, currentPlaylist.value ?: PlaylistWithMusic(
                playlist = MyPlaylists(0, null, context.getString(R.string.sem_nada)),
                mutableListOf()
            ), this@ContextMain
        )
    }

    fun setCurrentPlaylist(playlistWithMusic: PlaylistWithMusic?) {
        _currentPlaylist.value = playlistWithMusic
    }

    fun getFilesSaved() {
        viewModelScope.launch {
            val playlists = dataBase?.service()?.getAllPlaylistsWithMusic()?.toTypedArray()

            if (playlists.isNullOrEmpty()) {
                // Crie a playlist "Minhas músicas" se não houver playlists
                dataBase?.service()
                    ?.createMyPlaylist(null, context.getString(R.string.minhas_musicas))
            } else {
                _myPlaylist.value = playlists
                _currentPlaylist.value = playlists[0]
            }

            setSoundPy()
            setSaved()
            routineMusic()
            this.cancel()
        }
    }

    fun stream(music: Music) {
        viewModelScope.launch {
            try {
                setMusic(music)
                val res = repository.stream(music.url)
                utils.getImg(music, context) {
                    music.bitImage = utils.compressBitmapToByteArray(it)
                    _soundPy.value?.stream(Uri.parse(res.result), music)
                }
                println(music)
            } catch (err: Exception) {
                Log.d("Error", "$err")
            } finally {
                this.cancel()
            }
        }
    }
}