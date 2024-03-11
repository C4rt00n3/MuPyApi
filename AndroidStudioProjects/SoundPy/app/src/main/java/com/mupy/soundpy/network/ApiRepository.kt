package com.mupy.soundpy.network

import com.mupy.soundpy.models.Musics
import com.mupy.soundpy.models.PlayListData
import com.mupy.soundpy.models.PlayLists
import com.mupy.soundpy.models.StreamYt
import okhttp3.ResponseBody

class ApiRepository {
    private val api = Api.YouTube.service

    suspend fun search(query: String): Musics {
        return api.serach(query)
    }

    suspend fun getPlaylists(query: String): ArrayList<PlayListData> {
        return api.getPlaylists(query)
    }

    suspend fun playlist(link: String): PlayLists {
        return api.playlist(link)
    }

    suspend fun download(link: String): ResponseBody {
        return api.download(link)
    }

    suspend fun stream(link: String): StreamYt {
        return api.stream(link)
    }
}