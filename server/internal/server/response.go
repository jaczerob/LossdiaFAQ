package server

type EmbedField struct {
	Name   string `json:"name"`
	Value  string `json:"value"`
	Inline bool   `json:"inline"`
}

type Embed struct {
	Title       string       `json:"title"`
	Description string       `json:"description"`
	Fields      []EmbedField `json:"fields,omitempty"`
}

type ReturnData struct {
	Embeds  []Embed `json:"embeds,omitempty"`
	Content string  `json:"content,omitempty"`
}
