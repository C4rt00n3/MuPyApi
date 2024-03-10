package com.mupy.soundpy.screens

import android.content.Context
import android.os.Build
import androidx.annotation.RequiresApi
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material3.IconButton
import androidx.compose.material3.IconButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.livedata.observeAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.mupy.soundpy.ContextMain
import com.mupy.soundpy.R
import com.mupy.soundpy.components.Progress
import com.mupy.soundpy.components.icons.rememberArrowCircleLeft
import com.mupy.soundpy.components.icons.rememberArrowCircleRight
import com.mupy.soundpy.components.icons.rememberMotionPhotosPaused
import com.mupy.soundpy.components.icons.rememberPlayCircle
import com.mupy.soundpy.database.MyPlaylists
import com.mupy.soundpy.database.PlaylistWithMusic
import com.mupy.soundpy.ui.theme.BrandColor
import com.mupy.soundpy.ui.theme.ColorWhite
import com.mupy.soundpy.ui.theme.TextColor2
import com.mupy.soundpy.utils.SoundPy
import com.mupy.soundpy.utils.Utils


@RequiresApi(Build.VERSION_CODES.P)
@Composable
fun MusicScreen(viewModel: ContextMain, context: Context) {
    val mute by viewModel.mute.observeAsState(false)
    val repeat by viewModel.repeat.observeAsState(false)
    val pause by viewModel.pause.observeAsState(false)
    val soundPy by viewModel.soundPy.observeAsState(
        SoundPy(
            context,
            PlaylistWithMusic(playlist = MyPlaylists(0, null, ""), music = mutableListOf()),
            viewModel
        )
    )

    val currentPosition by viewModel.currentPosition.observeAsState(0)
    val utils = Utils()
    val music by viewModel.music.observeAsState(null)

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .fillMaxHeight()
            .background(BrandColor),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.SpaceEvenly
    ) {
        Spacer(modifier = Modifier.height(60.dp))
        Text(
            text = stringResource(R.string.play_now),
            fontSize = 24.sp,
            fontWeight = FontWeight.W500,
            color = Color.Black,
            modifier = Modifier.fillMaxWidth(),
            textAlign = TextAlign.Center
        )
        Column(
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            if (music?.bitImage == null) Image(
                painter = painterResource(id = R.mipmap.deadpoll),
                contentDescription = "Imagem da musica",
                modifier = Modifier
                    .widthIn(min = 250.dp, max = 250.dp)
                    .heightIn(min = 250.dp, max = 250.dp)
                    .padding(bottom = 16.dp),
                contentScale = ContentScale.Crop,
            )
            else utils.toBitmap(music?.bitImage)?.let {
                Image(
                    bitmap = it.asImageBitmap(),
                    contentDescription = "Imagem da musica",
                    modifier = Modifier
                        .widthIn(min = 250.dp, max = 350.dp)
                        .heightIn(min = 250.dp, max = 350.dp)
                        .padding(bottom = 16.dp),
                    contentScale = ContentScale.Crop,
                )
            }
            Text(
                text = music?.title ?: stringResource(id = R.string.carregando),
                fontWeight = FontWeight.Bold,
                color = ColorWhite,
                fontSize = 24.sp,
                modifier = Modifier
                    .padding(bottom = 16.dp)
                    .widthIn(max = (LocalConfiguration.current.screenWidthDp * 0.8).dp),
                overflow = TextOverflow.Ellipsis,
                maxLines = 1
            )
            Text(
                text = music?.author ?: stringResource(id = R.string.carregando),
                fontWeight = FontWeight.Medium,
                color = TextColor2,
                fontSize = 16.sp,
                modifier = Modifier
                    .padding(bottom = 16.dp)
                    .widthIn(max = (LocalConfiguration.current.screenWidthDp * 0.8).dp),
                overflow = TextOverflow.Ellipsis,
                maxLines = 1
            )

        }
        Row(
            horizontalArrangement = Arrangement.SpaceBetween,
            modifier = Modifier
                .fillMaxWidth()
                .height(50.dp)
        ) {
            IconButton(
                onClick = { viewModel.setRepeat(!repeat) },
                colors = IconButtonDefaults.iconButtonColors(contentColor = ColorWhite)
            ) {
                Image(
                    painter = painterResource(id = R.drawable.eva_shuffle_outline),
                    contentDescription = "Deixar musica no mudo.",
                    modifier = Modifier.size(20.dp),
                    alpha = if (!repeat) 1f else 0.5f
                )
            }
            Row {
                IconButton(
                    onClick = { viewModel.setMute(!mute) },
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.volume_1),
                        contentDescription = "Deixar musica no mudo.",
                        modifier = Modifier.size(20.dp),
                        alpha = if (mute) 1f else 0.5f
                    )
                }
                IconButton(
                    onClick = { viewModel.setRepeat(!repeat) },
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.ic_round_repeat),
                        contentDescription = "Deixar musica no mudo.",
                        modifier = Modifier.size(20.dp),
                        alpha = if (repeat) 1f else 0.5f
                    )
                }
            }
        }
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = soundPy.timeUse(currentPosition),
                    fontSize = 14.sp,
                    fontWeight = FontWeight.W400,
                    color = TextColor2
                )
                Text(
                    text = soundPy.timeUse(soundPy.player.duration.toInt()),
                    fontSize = 14.sp,
                    fontWeight = FontWeight.W400,
                    color = TextColor2
                )
            }
            Spacer(modifier = Modifier.height(16.dp))
            Progress(
                viewModel = viewModel
            )
        }
        Row(
            verticalAlignment = Alignment.CenterVertically,
        ) {
            IconButton(
                onClick = {
                    @Suppress("DEPRECATION")
                    soundPy.player.previous()
                }, modifier = Modifier.size(60.dp)
            ) {
                Image(
                    modifier = Modifier.fillMaxSize(),
                    imageVector = rememberArrowCircleLeft(),
                    contentDescription = stringResource(R.string.ir_para_musica_passada),
                )
            }
            Spacer(modifier = Modifier.width(30.dp))
            IconButton(
                onClick = {
                    if (!pause) {
                        soundPy.player.play()
                    } else {
                        soundPy.player.pause()
                    }
                    viewModel.setPause(soundPy.player.isPlaying)
                    viewModel.startTime()
                }, modifier = Modifier.size(60.dp)
            ) {
                Image(
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop,
                    imageVector = if (pause) rememberMotionPhotosPaused() else rememberPlayCircle(),
                    contentDescription = stringResource(R.string.ir_para_musica_passada),
                )
            }
            Spacer(modifier = Modifier.width(30.dp))
            IconButton(modifier = Modifier.size(60.dp), onClick = {
                @Suppress("DEPRECATION")
                soundPy.player.next()
            }) {
                Image(
                    modifier = Modifier.fillMaxSize(),
                    imageVector = rememberArrowCircleRight(),
                    contentDescription = stringResource(R.string.ir_para_musica_passada),
                )
            }
        }
    }
}