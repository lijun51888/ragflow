import Image from '@/components/image';
import SvgIcon from '@/components/svg-icon';
import { IReference, IReferenceChunk } from '@/interfaces/database/chat';
import { getExtension } from '@/utils/document-util';
import { InfoCircleOutlined } from '@ant-design/icons';
import { Button, Flex, Popover } from 'antd';
import DOMPurify from 'dompurify';
import { useCallback, useEffect, useMemo } from 'react';
import Markdown from 'react-markdown';
import reactStringReplace from 'react-string-replace';
import SyntaxHighlighter from 'react-syntax-highlighter';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import { visitParents } from 'unist-util-visit-parents';

import { useFetchDocumentThumbnailsByIds } from '@/hooks/document-hooks';
import { useTranslation } from 'react-i18next';

import 'katex/dist/katex.min.css'; // `rehype-katex` does not import the CSS for you

import { preprocessLaTeX, replaceThinkToSection } from '@/utils/chat';
import { replaceTextByOldReg } from '../utils';

import classNames from 'classnames';
import { pipe } from 'lodash/fp';
import styles from './index.less';

const reg = /(~{2}\d+={2})/g;
// const curReg = /(~{2}\d+\${2})/g;

// 自定义插件用于解析图片尺寸
const remarkImageSize = () => {
  const processNode = (node, index, parentChildren) => {
    if (node.type === 'image') {
      // 检查下一个节点是否为 text 类型且包含尺寸信息
      if (index + 1 < parentChildren.length) {
        const nextNode = parentChildren[index + 1];
        if (nextNode.type === 'text') {
          const match = nextNode.value.match(
            /\{width="([^"]+)" height="([^"]+)"\}/,
          );
          if (match) {
            const [, width, height] = match;
            node.attributes = node.attributes || [];
            node.attributes.push({
              type: 'attribute',
              name: 'width',
              value: width,
            });
            node.attributes.push({
              type: 'attribute',
              name: 'height',
              value: height,
            });
            // 移除包含尺寸信息的 text 节点
            parentChildren.splice(index + 1, 1);
          }
        }
      }
    }
    if (node.children && Array.isArray(node.children)) {
      node.children.forEach((childNode, childIndex) =>
        processNode(childNode, childIndex, node.children),
      );
    }
  };

  return (tree) => {
    tree.children.forEach((node, index) =>
      processNode(node, index, tree.children),
    );
  };
};

const getChunkIndex = (match: string) => Number(match.slice(2, -2));
// TODO: The display of the table is inconsistent with the display previously placed in the MessageItem.
const MarkdownContent = ({
  reference,
  clickDocumentButton,
  content,
}: {
  content: string;
  loading: boolean;
  reference: IReference;
  clickDocumentButton?: (documentId: string, chunk: IReferenceChunk) => void;
}) => {
  const { t } = useTranslation();
  const { setDocumentIds, data: fileThumbnails } =
    useFetchDocumentThumbnailsByIds();
  const contentWithCursor = useMemo(() => {
    let text = content;
    if (text === '') {
      text = t('chat.searching');
    }
    const nextText = replaceTextByOldReg(text);
    return pipe(replaceThinkToSection, preprocessLaTeX)(nextText);
  }, [content, t]);

  useEffect(() => {
    const docAggs = reference?.doc_aggs;
    setDocumentIds(Array.isArray(docAggs) ? docAggs.map((x) => x.doc_id) : []);
  }, [reference, setDocumentIds]);

  const handleDocumentButtonClick = useCallback(
    (
      documentId: string,
      chunk: IReferenceChunk,
      isPdf: boolean,
      documentUrl?: string,
    ) =>
      () => {
        if (!isPdf) {
          if (!documentUrl) {
            return;
          }
          window.open(documentUrl, '_blank');
        } else {
          clickDocumentButton?.(documentId, chunk);
        }
      },
    [clickDocumentButton],
  );

  const rehypeWrapReference = () => {
    return function wrapTextTransform(tree: any) {
      visitParents(tree, 'text', (node, ancestors) => {
        const latestAncestor = ancestors.at(-1);
        if (
          latestAncestor.tagName !== 'custom-typography' &&
          latestAncestor.tagName !== 'code'
        ) {
          node.type = 'element';
          node.tagName = 'custom-typography';
          node.properties = {};
          node.children = [{ type: 'text', value: node.value }];
        }
      });
    };
  };

  const getPopoverContent = useCallback(
    (chunkIndex: number) => {
      const chunks = reference?.chunks ?? [];
      const chunkItem = chunks[chunkIndex];
      const document = reference?.doc_aggs?.find(
        (x) => x?.doc_id === chunkItem?.document_id,
      );
      const documentId = document?.doc_id;
      const documentUrl = document?.url;
      const fileThumbnail = documentId ? fileThumbnails[documentId] : '';
      const fileExtension = documentId ? getExtension(document?.doc_name) : '';
      const imageId = chunkItem?.image_id;
      return (
        <div key={chunkItem?.id} className="flex gap-2">
          {imageId && (
            <Popover
              placement="left"
              content={
                <Image
                  id={imageId}
                  className={styles.referenceImagePreview}
                ></Image>
              }
            >
              <Image
                id={imageId}
                className={styles.referenceChunkImage}
              ></Image>
            </Popover>
          )}
          <div className={'space-y-2 max-w-[40vw]'}>
            <div
              dangerouslySetInnerHTML={{
                __html: DOMPurify.sanitize(chunkItem?.content ?? ''),
              }}
              className={classNames(styles.chunkContentText)}
            ></div>
            {documentId && (
              <Flex gap={'small'}>
                {fileThumbnail ? (
                  <img
                    src={fileThumbnail}
                    alt=""
                    className={styles.fileThumbnail}
                  />
                ) : (
                  <SvgIcon
                    name={`file-icon/${fileExtension}`}
                    width={24}
                  ></SvgIcon>
                )}
                <Button
                  type="link"
                  className={classNames(styles.documentLink, 'text-wrap')}
                  onClick={handleDocumentButtonClick(
                    documentId,
                    chunkItem,
                    fileExtension === 'pdf',
                    documentUrl,
                  )}
                >
                  {document?.doc_name}
                </Button>
              </Flex>
            )}
          </div>
        </div>
      );
    },
    [reference, fileThumbnails, handleDocumentButtonClick],
  );

  const renderReference = useCallback(
    (text: string) => {
      let replacedText = reactStringReplace(text, reg, (match, i) => {
        const chunkIndex = getChunkIndex(match);
        return (
          <Popover content={getPopoverContent(chunkIndex)} key={i}>
            <InfoCircleOutlined className={styles.referenceIcon} />
          </Popover>
        );
      });

      // replacedText = reactStringReplace(replacedText, curReg, (match, i) => (
      //   <span className={styles.cursor} key={i}></span>
      // ));

      return replacedText;
    },
    [getPopoverContent],
  );

  // 自定义图片渲染组件
  const ImageRenderer = ({ node }) => {
    const attributes = {};
    if (node.attributes) {
      node.attributes.forEach((attr) => {
        attributes[attr.name] = attr.value;
      });
    }
    const convertToPx = (value) => {
      if (typeof value === 'string' && value.endsWith('in')) {
        // 假设 1 英寸 = 96 像素
        const inches = parseFloat(value.slice(0, -2));
        return `${inches * 96}px`;
      }
      return value;
    };
    const style = {
      width: convertToPx(attributes.width) || 'auto',
      height: convertToPx(attributes.height) || 'auto',
    };
    return (
      <img
        src={node.url}
        alt={node.alt}
        style={style}
        className={styles.maxSize200}
        {...attributes}
      />
    );
  };

  return (
    <Markdown
      rehypePlugins={[rehypeWrapReference, rehypeKatex, rehypeRaw]}
      remarkPlugins={[remarkGfm, remarkMath, remarkImageSize]}
      className={styles.markdownContentWrapper}
      components={
        {
          image: ImageRenderer,
          'custom-typography': ({ children }: { children: string }) =>
            renderReference(children),
          code(props: any) {
            const { children, className, node, ...rest } = props;
            const match = /language-(\w+)/.exec(className || '');
            return match ? (
              <SyntaxHighlighter
                {...rest}
                PreTag="div"
                language={match[1]}
                wrapLongLines
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code {...rest} className={classNames(className, 'text-wrap')}>
                {children}
              </code>
            );
          },
        } as any
      }
    >
      {contentWithCursor}
    </Markdown>
  );
};

export default MarkdownContent;
