use serde::{Deserialize, Serialize};

fn main() {
    #[derive(Debug, Clone, Serialize, Deserialize)]
    #[serde(rename_all = "PascalCase")]
    pub struct Song {
        pub title: String,
        pub composer: Option<String>,
        pub key: Option<String>,
        pub rhythm: Option<String>,
        pub time_signature: Option<String>,
        pub sections: Option<Vec<Section>>,
    }

    #[derive(Debug, Clone, Serialize, Deserialize)]
    #[serde(rename_all = "PascalCase")]
    pub struct Section {
        pub label: Option<String>,
        pub repeats: Option<u32>,
        pub main_segment: Option<Segment>,
    }

    #[derive(Debug, Clone, Serialize, Deserialize)]
    #[serde(rename_all = "PascalCase")]
    pub struct Segment {
        pub chords: Option<String>,
    }
}
