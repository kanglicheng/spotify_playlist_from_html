import argparse
import pandas as pd

# local
import utils
from spotify_abs_cls import SpotifyHandler

# constants
IS_PUBLIC_PLAYLIST = True

def parse_args():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--spotify-yaml-path', '-s', help='Spotify credentials file',
                        default='./spotify.yaml', type=str)
    parser.add_argument('--html-file-path', '-f', type=str, help='HTML file path',
                        default='bidud_party.html', )
    parser.add_argument('--playlist-name', '-n', type=str, default='Bidud Party Tests', help='Playlist name')
    parser.add_argument('--playlist-description', '-d', type=str, default='Yayz', help='Playlist description')
    return parser.parse_args()


class HtmlToPlaylist(SpotifyHandler):
    """
    Create playlist from a given HTML page.
    """

    IS_PUBLIC_PLAYLIST = True

    def __init__(self, spotify_yaml_path, html_file_path, playlist_name, playlist_description):
        """
        see the parse_args function for documentation on the parameters.
        """
        self._html_file_path = html_file_path
        self._playlist_name = playlist_name
        self._playlist_description = playlist_description
        #
        super().__init__(spotify_yaml_path)
        self._sp.trace = False

    def run(self):
        with open(self._html_file_path, 'rb') as fid:
            html_text = fid.read()
        tables = pd.read_html(html_text)
        playlist_table = tables[0]
        playlist_table = playlist_table.rename(columns=playlist_table.iloc[0])
        playlist_table = playlist_table.drop(playlist_table.index[0])

        tracks = []
        for index, row in playlist_table.iterrows():
            song_uri_thinger = utils.get_song(self._sp, name=row['Title'], artist=row['Artist'], album=row['Release'])
            if song_uri_thinger is None:
                print(f"Skipping [{row['Artist']} - {row['Title']}]")
                continue
            tracks.append(song_uri_thinger)

        track_infos_no_dup = utils.remove_duplicates_keep_order(tracks)
        track_ids = utils.track_ids_from_infos(track_infos_no_dup)

        playlist_url = utils.create_playlist_from_track_ids(self._sp,
                                                            self._user_id,
                                                            self._playlist_name,
                                                            self._playlist_description,
                                                            IS_PUBLIC_PLAYLIST,
                                                            track_ids)

        print(f"Success: Playlist URL at {playlist_url}")


def main():
    args = parse_args()
    html_to_playlist_obj = HtmlToPlaylist(**vars(args))
    html_to_playlist_obj.run()


if __name__ == '__main__':
    main()
