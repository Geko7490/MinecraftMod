use horizon_mods::{Content, Package};
use std::path::Path;

fn main() {
    let files: Vec<_> = std::env::args().skip(1).collect();
    assert!(!files.is_empty(), "pass the generated HMOD paths");
    for file in files {
        let path = Path::new(&file);
        let package = Package::read(path).unwrap_or_else(|error| panic!("{file}: {error}"));
        let content = Content::read(path, &package.manifest)
            .unwrap_or_else(|error| panic!("{file}: {error}"));
        println!("Validated {file}: {} content files", content.files.len());
    }
}
